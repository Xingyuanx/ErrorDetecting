import app.log_collector as lc
import app.log_reader as lr

def test_parse_and_save_chunk_mock():
    sample_lines = [
        "[2024-12-17 10:00:00,123] INFO org.apache.hadoop.hdfs.server.datanode.DataNode: Started",
        "[2024-12-17 10:01:00,456] WARN org.apache.hadoop.hdfs.server.datanode.DataNode: Disk nearly full",
        "[2024-12-17 10:02:00,789] ERROR org.apache.hadoop.hdfs.server.datanode.DataNode: Write failed",
        "Plain line without timestamp INFO something",
        "",
    ]
    content = "\n".join(sample_lines)

    captured = []

    async def _fake_save_logs_to_db_batch(items: list[dict]):
        captured.extend(items)

    # monkeypatch batch save method
    lc.log_collector._save_logs_to_db_batch = _fake_save_logs_to_db_batch

    # run save chunk
    lc.log_collector._save_log_chunk("hadoop102", "datanode", content)

    # verify non-empty lines saved
    expected_saved = [ln for ln in sample_lines if ln.strip()]
    assert len(captured) == len(expected_saved)
    # check fields
    for item in captured:
        assert item["host"] == "hadoop102"
        assert item["service"] == "datanode"
        assert isinstance(item["message"], str) and item["message"]
        assert item["log_level"] in {"INFO", "WARN", "ERROR", "DEBUG", "TRACE"}
        assert getattr(item["timestamp"], "tzinfo", None) is not None

def test_log_file_path_namenode():
    p = lr.log_reader.get_log_file_path("hadoop102", "namenode")
    assert p.endswith("/hadoop-hadoop-namenode-hadoop102.log")
