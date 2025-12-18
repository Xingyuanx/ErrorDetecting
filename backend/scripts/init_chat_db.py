import asyncio
import os
import sys

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.db import engine
from backend.app.models.chat import Base as ChatBase

async def init_db():
    async with engine.begin() as conn:
        print("Dropping chat tables if exist...")
        await conn.run_sync(ChatBase.metadata.drop_all)
        print("Creating chat tables...")
        await conn.run_sync(ChatBase.metadata.create_all)
        print("Done.")

if __name__ == "__main__":
    asyncio.run(init_db())
