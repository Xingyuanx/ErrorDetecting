from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db

router = APIRouter()

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """健康检查：测试数据库连通性。"""
    await db.execute("SELECT 1")
    return {"status": "ok"}