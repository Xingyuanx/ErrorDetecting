import asyncio
import os
from sqlalchemy import text
from app.db import engine

async def main():
    uuid = os.environ.get("CLUSTER_UUID")
    async with engine.begin() as conn:
        cid = None
        if uuid:
            res = await conn.execute(text("SELECT id FROM clusters WHERE uuid=:u LIMIT 1"), {"u": uuid})
            row = res.first()
            cid = row[0] if row else None
        if cid:
            res1 = await conn.execute(text("SELECT COUNT(*) FROM nodes WHERE cluster_id=:cid AND last_heartbeat IS NOT NULL"), {"cid": cid})
        else:
            res1 = await conn.execute(text("SELECT COUNT(*) FROM nodes WHERE last_heartbeat IS NOT NULL"))
        c1 = res1.scalar() or 0
        print('NODES_WITH_HEARTBEAT_BEFORE', c1)
    await asyncio.sleep(10)
    async with engine.begin() as conn:
        if cid:
            res2 = await conn.execute(text("SELECT COUNT(*) FROM nodes WHERE cluster_id=:cid AND last_heartbeat IS NOT NULL"), {"cid": cid})
            res3 = await conn.execute(text("SELECT hostname, cpu_usage, memory_usage, last_heartbeat FROM nodes WHERE cluster_id=:cid ORDER BY last_heartbeat DESC NULLS LAST LIMIT 5"), {"cid": cid})
            avg = await conn.execute(text("SELECT AVG(cpu_usage), AVG(memory_usage) FROM nodes WHERE cluster_id=:cid"), {"cid": cid})
        else:
            res2 = await conn.execute(text("SELECT COUNT(*) FROM nodes WHERE last_heartbeat IS NOT NULL"))
            res3 = await conn.execute(text("SELECT hostname, cpu_usage, memory_usage, last_heartbeat FROM nodes ORDER BY last_heartbeat DESC NULLS LAST LIMIT 5"))
            avg = await conn.execute(text("SELECT AVG(cpu_usage), AVG(memory_usage) FROM nodes"))
        c2 = res2.scalar() or 0
        print('NODES_WITH_HEARTBEAT_AFTER', c2)
        for row in res3.all():
            print('NODE', row)
        ar = avg.first()
        print('CLUSTER_AVG', float(ar[0] or 0.0), float(ar[1] or 0.0))

if __name__ == '__main__':
    asyncio.run(main())
