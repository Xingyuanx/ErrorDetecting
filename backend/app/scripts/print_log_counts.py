import asyncio
from sqlalchemy import text
from app.db import engine

async def main():
    async with engine.begin() as conn:
        c = await conn.execute(text('SELECT COUNT(*) FROM hadoop_logs'))
        print('HADOOP_LOGS_COUNT', c.scalar() or 0)
        rows = await conn.execute(text('SELECT cluster_name,node_host,title,log_time FROM hadoop_logs ORDER BY log_id DESC LIMIT 5'))
        for r in rows.all():
            print('LOG', r)

if __name__ == "__main__":
    asyncio.run(main())
