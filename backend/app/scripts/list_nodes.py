import asyncio
from sqlalchemy import text
from app.db import engine

async def main():
    async with engine.begin() as conn:
        res = await conn.execute(text('SELECT id, hostname, cpu_usage, memory_usage, last_heartbeat FROM nodes ORDER BY id LIMIT 5'))
        for row in res.all():
            print('NODE', row)

if __name__ == '__main__':
    asyncio.run(main())
