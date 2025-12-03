from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_db
from ..models.fault_records import FaultRecord

router = APIRouter()

@router.get("/faults")
async def list_faults(db: AsyncSession = Depends(get_db)):
    """查询故障记录。"""
    result = await db.execute(select(FaultRecord).limit(100))
    rows = result.scalars().all()
    return {"total": len(rows), "list": [f.to_dict() for f in rows]}