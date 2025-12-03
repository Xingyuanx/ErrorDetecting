from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_db
from ..models.system_logs import SystemLog

router = APIRouter()

@router.get("/logs")
async def list_logs(
    db: AsyncSession = Depends(get_db),
    level: str | None = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
):
    """查询系统日志，支持按级别筛选与分页。"""
    stmt = select(SystemLog)
    if level:
        stmt = stmt.where(SystemLog.log_level == level)
    stmt = stmt.offset((page - 1) * pageSize).limit(pageSize)
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return {"total": len(rows), "list": [l.to_dict() for l in rows]}