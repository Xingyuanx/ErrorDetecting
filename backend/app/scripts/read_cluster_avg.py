import os
import asyncio
from sqlalchemy import text
from app.db import engine

async def main():
    uuid = os.environ.get("CLUSTER_UUID")
    async with engine.begin() as conn:
        if uuid:
            res = await conn.execute(text("SELECT cpu_avg, memory_avg FROM clusters WHERE uuid=:u LIMIT 1"), {"u": uuid})
        else:
            res = await conn.execute(text("SELECT cpu_avg, memory_avg FROM clusters LIMIT 1"))
        row = res.first()
        print("CLUSTER_AVG_STORED", (float(row[0]) if row and row[0] is not None else 0.0), (float(row[1]) if row and row[1] is not None else 0.0))

if __name__ == "__main__":
    asyncio.run(main())
