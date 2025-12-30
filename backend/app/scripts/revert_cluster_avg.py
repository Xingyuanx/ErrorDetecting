import asyncio
from sqlalchemy import text
from app.db import engine

async def main():
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE clusters DROP COLUMN IF EXISTS cpu_avg"))
        await conn.execute(text("ALTER TABLE clusters DROP COLUMN IF EXISTS memory_avg"))
        await conn.execute(text("ALTER TABLE clusters DROP COLUMN IF EXISTS last_avg_at"))

if __name__ == "__main__":
    asyncio.run(main())
