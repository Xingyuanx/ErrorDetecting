import asyncio
import argparse
from sqlalchemy import select
from app.db import SessionLocal
from app.models.nodes import Node
from app.models.clusters import Cluster
from app.metrics_collector import metrics_collector

async def collect_once(cluster_uuid: str):
    async with SessionLocal() as session:
        cid_res = await session.execute(select(Cluster.id).where(Cluster.uuid == cluster_uuid).limit(1))
        cid = cid_res.scalars().first()
        if not cid:
            return
        res = await session.execute(select(Node.id, Node.hostname, Node.ip_address).where(Node.cluster_id == cid))
        rows = res.all()
        for nid, hn, ip in rows:
            cpu, mem = metrics_collector._read_cpu_mem(hn, str(ip))
            await metrics_collector._save_metrics(nid, hn, cid, cpu, mem)

async def runner(cluster_uuid: str, interval: int):
    while True:
        try:
            await collect_once(cluster_uuid)
        except Exception:
            pass
        await asyncio.sleep(interval)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cluster", required=True, help="Cluster UUID to collect metrics for")
    parser.add_argument("--interval", type=int, default=3, help="Collect interval seconds")
    args = parser.parse_args()
    metrics_collector.set_collection_interval(args.interval)
    asyncio.run(runner(args.cluster, args.interval))

if __name__ == "__main__":
    main()
