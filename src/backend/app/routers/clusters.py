from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_db
from ..models.clusters import Cluster

router = APIRouter()

@router.get("/clusters")
async def list_clusters(db: AsyncSession = Depends(get_db)):
    """查询集群列表。"""
    result = await db.execute(select(Cluster).limit(100))
    rows = result.scalars().all()
    return {"total": len(rows), "list": [c.to_dict() for c in rows]}