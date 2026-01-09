import pytest
from app.services.hadoop_cluster_uuid import collect_cluster_uuid

class _CliOK:
    def __init__(self, host, user, pwd):
        pass
    def execute_command_with_timeout(self, cmd, timeout):
        if "getconf" in cmd or "awk" in cmd:
            return ("/data/hdfs/namenode", "")
        if "VERSION" in cmd:
            return ("clusterID=12345-abc", "")
        return ("", "")
    def close(self):
        pass

class _CliNoDirs:
    def __init__(self, host, user, pwd):
        pass
    def execute_command_with_timeout(self, cmd, timeout):
        return ("", "")
    def close(self):
        pass

def test_collect_cluster_uuid_success(monkeypatch):
    monkeypatch.setattr("app.services.hadoop_cluster_uuid.SSHClient", lambda h,u,p: _CliOK(h,u,p))
    u, step, detail = collect_cluster_uuid("10.0.0.1", "u", "p")
    assert u is not None
    assert step is None
    assert detail is None

def test_collect_cluster_uuid_fail_no_dirs(monkeypatch):
    monkeypatch.setattr("app.services.hadoop_cluster_uuid.SSHClient", lambda h,u,p: _CliNoDirs(h,u,p))
    u, step, detail = collect_cluster_uuid("10.0.0.1", "u", "p")
    assert u is None
    assert step == "probe_name_dirs"
