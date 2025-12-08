from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, or_
from ..db import get_db
from ..models.system_logs import SystemLog
from ..models.clusters import Cluster
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
    level: str | None = Query(None),
    cluster: str | None = Query(None),
    node: str | None = Query(None),
    op: str | None = Query(None),
    source: str | None = Query(None),
    time_from: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
):
    try:
        name = _get_username(user)
        stmt = select(SystemLog)
        count_stmt = select(func.count(SystemLog.id))

        filters = []
        if level:
            level_up = level.upper()
            filters.append(SystemLog.log_level == level_up)
        if cluster:
            cid_res = await db.execute(select(Cluster.id).where(Cluster.uuid == cluster).limit(1))
            cid = cid_res.scalars().first()
            if cid:
                filters.append(SystemLog.cluster_id == cid)
            else:
                return {"items": [], "total": 0}
        if node:
            filters.append(SystemLog.host == node)
        if op:
            filters.append(SystemLog.service == op)
        if source:
            like = f"%{source}%"
            filters.append(or_(SystemLog.source.ilike(like), SystemLog.service.ilike(like), SystemLog.host.ilike(like)))
        tf = _parse_time(time_from)
        if tf:
            filters.append(SystemLog.timestamp >= tf)

        for f in filters:
            stmt = stmt.where(f)
            count_stmt = count_stmt.where(f)

        stmt = stmt.order_by(SystemLog.timestamp.desc()).offset((page - 1) * size).limit(size)
        rows = (await db.execute(stmt)).scalars().all()
        total = (await db.execute(count_stmt)).scalar() or 0

        # 预取集群UUID映射
        cid_set = {r.cluster_id for r in rows if r.cluster_id is not None}
        uuid_map: dict[int, str] = {}
        if cid_set:
            res = await db.execute(select(Cluster.id, Cluster.uuid).where(Cluster.id.in_(list(cid_set))))
            uuid_map = {rid: str(u) for rid, u in res.all()}

        items = [
            {
                "id": r.id,
                "time": r.timestamp.isoformat() if r.timestamp else None,
                "level": (r.log_level or "").lower(),
                "cluster": uuid_map.get(r.cluster_id),
                "node": r.host,
                "op": r.service,
                "user": "system",
                "source": r.source,
                "message": r.message,
            }
            for r in rows
        ]
        return {"items": items, "total": int(total)}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


@router.get("/logs/meta")
async def logs_meta(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        # clusters: 有日志的集群 UUID 集合
        cid_res = await db.execute(select(SystemLog.cluster_id).where(SystemLog.cluster_id.is_not(None)))
        cids = {cid for cid in cid_res.scalars().all() if cid is not None}
        clusters: list[str] = []
        if cids:
            res = await db.execute(select(Cluster.uuid).where(Cluster.id.in_(list(cids))))
            clusters = [str(u) for (u,) in res.all()]
        # nodes: 主机集合
        host_res = await db.execute(select(SystemLog.host).where(SystemLog.host.is_not(None)))
        nodes = sorted({h for h in host_res.scalars().all() if h})
        # ops: 服务集合
        svc_res = await db.execute(select(SystemLog.service).where(SystemLog.service.is_not(None)))
        ops = sorted({s for s in svc_res.scalars().all() if s})
        return {"clusters": clusters, "nodes": nodes, "ops": ops}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")
