import os
import asyncio
import time
from sqlalchemy import select, text
from app.db import SessionLocal, engine
from app.models.clusters import Cluster
from app.models.nodes import Node
from app.log_reader import log_reader
from app.log_collector import log_collector

async def run(cluster_uuid: str, interval: int = 3, duration: int = 10):
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT id FROM clusters WHERE uuid=:u LIMIT 1"), {"u": cluster_uuid})
        row = res.first()
        if not row:
            print("CLUSTER_NOT_FOUND")
            return
        cid = row[0]
        before = await conn.execute(text("SELECT COUNT(*) FROM hadoop_logs"))
        print("HADOOP_LOGS_BEFORE", before.scalar() or 0)
    async with SessionLocal() as session:
        nodes_res = await session.execute(select(Node.hostname, Node.ip_address).where(Node.cluster_id == cid))
        nodes = [(r[0], str(r[1])) for r in nodes_res.all()]
    started = []
    for hn, ip in nodes:
        try:
            log_reader.find_working_log_dir(hn, ip)
            files = log_reader.get_log_files_list(hn, ip=ip)
        except Exception:
            files = []
        services = set()
        for f in files:
            lf = f.lower()
            if "namenode" in lf:
                services.add("namenode")
            elif "secondarynamenode" in lf:
                services.add("secondarynamenode")
            elif "datanode" in lf:
                services.add("datanode")
            elif "resourcemanager" in lf:
                services.add("resourcemanager")
            elif "nodemanager" in lf:
                services.add("nodemanager")
            elif "historyserver" in lf:
                services.add("historyserver")
        for t in services:
            ok = log_collector.start_collection(hn, t, ip=ip, interval=interval)
            if ok:
                started.append(f"{hn}_{t}")
    time.sleep(duration)
    log_collector.stop_all_collections()
    async with engine.begin() as conn:
        after = await conn.execute(text("SELECT COUNT(*) FROM hadoop_logs"))
        print("HADOOP_LOGS_AFTER", after.scalar() or 0)
        last = await conn.execute(text("SELECT cluster_name, node_host, title, log_time FROM hadoop_logs ORDER BY log_id DESC LIMIT 5"))
        for row in last.all():
            print("LOG", row)

def main():
    uuid = os.environ.get("CLUSTER_UUID")
    interval = int(os.environ.get("LOG_INTERVAL", "3"))
    duration = int(os.environ.get("LOG_DURATION", "10"))
    asyncio.run(run(uuid, interval=interval, duration=duration))

if __name__ == "__main__":
    main()
