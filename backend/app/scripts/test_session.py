import asyncio
from sqlalchemy import text
from app.db import SessionLocal

async def main():
    async with SessionLocal() as session:
        res = await session.execute(text('SELECT 1'))
        print('OK', res.scalar())

if __name__ == '__main__':
    asyncio.run(main())
