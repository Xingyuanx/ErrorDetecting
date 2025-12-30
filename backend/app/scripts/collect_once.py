import asyncio
import argparse
from sqlalchemy import select
from app.db import SessionLocal
from app.models.nodes import Node
from app.models.clusters import Cluster
from app.metrics_collector import metrics_collector

async def run(uuid: str):
    async with SessionLocal() as session:
        cid_res = await session.execute(select(Cluster.id).where(Cluster.uuid == uuid).limit(1))
        cid = cid_res.scalars().first()
        if not cid:
            print("NO_CLUSTER")
            return
        res = await session.execute(select(Node.id, Node.hostname, Node.ip_address).where(Node.cluster_id == cid))
        rows = res.all()
        if not rows:
            print("NO_NODES")
            return
        for nid, hn, ip in rows:
            cpu, mem = metrics_collector._read_cpu_mem(hn, str(ip))
            await metrics_collector._save_metrics(nid, hn, cid, cpu, mem)
        print("DONE", len(rows))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cluster", required=True)
    args = parser.parse_args()
    asyncio.run(run(args.cluster))

if __name__ == "__main__":
    main()
