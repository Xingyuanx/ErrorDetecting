import os
import asyncio
from sqlalchemy import text
from app.db import engine

async def main():
    uuid = os.environ.get("CLUSTER_UUID")
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE clusters ADD COLUMN IF NOT EXISTS cpu_avg double precision"))
        await conn.execute(text("ALTER TABLE clusters ADD COLUMN IF NOT EXISTS memory_avg double precision"))
        await conn.execute(text("ALTER TABLE clusters ADD COLUMN IF NOT EXISTS last_avg_at timestamptz"))
    async with engine.begin() as conn:
        if uuid:
            res = await conn.execute(text("SELECT id FROM clusters WHERE uuid=:u LIMIT 1"), {"u": uuid})
            row = res.first()
            if row:
                cid = row[0]
                avg = await conn.execute(text("SELECT AVG(cpu_usage), AVG(memory_usage) FROM nodes WHERE cluster_id=:cid"), {"cid": cid})
                ar = avg.first()
                await conn.execute(text("UPDATE clusters SET cpu_avg=:ca, memory_avg=:ma, last_avg_at=NOW() WHERE id=:cid"), {"ca": float(ar[0] or 0.0), "ma": float(ar[1] or 0.0), "cid": cid})
        else:
            avg = await conn.execute(text("SELECT AVG(cpu_usage), AVG(memory_usage) FROM nodes"))
            ar = avg.first()
            await conn.execute(text("UPDATE clusters SET cpu_avg=:ca, memory_avg=:ma, last_avg_at=NOW()"), {"ca": float(ar[0] or 0.0), "ma": float(ar[1] or 0.0)})

if __name__ == "__main__":
    asyncio.run(main())
