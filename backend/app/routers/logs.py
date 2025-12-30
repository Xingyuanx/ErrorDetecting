from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from ..db import get_db
from ..models.hadoop_logs import HadoopLog
from ..deps.auth import get_current_user
from datetime import datetime, timezone

router = APIRouter()


def _get_username(u) -> str:
    return getattr(u, "username", None) or (u.get("username") if isinstance(u, dict) else None)


def _parse_time(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)
    except Exception:
        return None


@router.get("/logs")
async def list_logs(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    cluster: str | None = Query(None),
    node: str | None = Query(None),
    source: str | None = Query(None),
    time_from: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
):
    try:
        stmt = select(HadoopLog)
        count_stmt = select(func.count(HadoopLog.log_id))

        filters = []
        if cluster:
            filters.append(HadoopLog.cluster_name == cluster)
        if node:
            filters.append(HadoopLog.node_host == node)
        if source:
            like = f"%{source}%"
            filters.append(or_(HadoopLog.title.ilike(like), HadoopLog.info.ilike(like), HadoopLog.node_host.ilike(like)))
        tf = _parse_time(time_from)
        if tf:
            filters.append(HadoopLog.log_time >= tf)

        for f in filters:
            stmt = stmt.where(f)
            count_stmt = count_stmt.where(f)

        stmt = stmt.order_by(HadoopLog.log_time.desc()).offset((page - 1) * size).limit(size)
        rows = (await db.execute(stmt)).scalars().all()
        total = (await db.execute(count_stmt)).scalar() or 0

        items = [
            {
                "id": r.log_id,
                "time": r.log_time.isoformat() if r.log_time else None,
                "cluster": r.cluster_name,
                "node": r.node_host,
                "title": r.title,
                "info": r.info,
            }
            for r in rows
        ]
        return {"items": items, "total": int(total)}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error listing logs: {e}")
        raise HTTPException(status_code=500, detail="server_error")
