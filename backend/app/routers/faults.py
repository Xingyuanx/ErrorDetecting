from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, update
from ..db import get_db
from ..models.system_logs import SystemLog
from ..models.clusters import Cluster
from ..deps.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime, timezone
import json

router = APIRouter()


def _get_username(u) -> str:
    return getattr(u, "username", None) or (u.get("username") if isinstance(u, dict) else None)


def _now():
    return datetime.now(timezone.utc)


def _map_level(level: str) -> str:
    lv = (level or "").lower()
    if lv in ("critical", "fatal"):
        return "FATAL"
    if lv == "high":
        return "ERROR"
    if lv == "medium":
        return "WARN"
    return "INFO"


class FaultCreate(BaseModel):
    id: str
    type: str
    level: str
    status: str
    title: str
    cluster: str | None = None
    node: str | None = None
    created: str | None = None


class FaultUpdate(BaseModel):
    status: str | None = None
    title: str | None = None


@router.get("/faults")
async def list_faults(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    cluster: str | None = Query(None),
    node: str | None = Query(None),
    time_from: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
):
    try:
        stmt = select(SystemLog).where(SystemLog.service == "fault")
        count_stmt = select(func.count(SystemLog.id)).where(SystemLog.service == "fault")

        if cluster:
            # 支持传 UUID 或名称
            cid_res = await db.execute(select(Cluster.id).where(Cluster.uuid == cluster).limit(1))
            cid = cid_res.scalars().first()
            if not cid:
                name_res = await db.execute(select(Cluster.id).where(Cluster.name == cluster).limit(1))
                cid = name_res.scalars().first()
            if cid:
                stmt = stmt.where(SystemLog.cluster_id == cid)
                count_stmt = count_stmt.where(SystemLog.cluster_id == cid)
            else:
                return {"items": [], "total": 0}
        if node:
            stmt = stmt.where(SystemLog.host == node)
            count_stmt = count_stmt.where(SystemLog.host == node)
        if time_from:
            try:
                tf = datetime.fromisoformat(time_from.replace("Z", "+00:00"))
                stmt = stmt.where(SystemLog.timestamp >= tf)
                count_stmt = count_stmt.where(SystemLog.timestamp >= tf)
            except Exception:
                pass

        stmt = stmt.order_by(SystemLog.timestamp.desc()).offset((page - 1) * size).limit(size)
        rows = (await db.execute(stmt)).scalars().all()
        total = (await db.execute(count_stmt)).scalar() or 0

        # 预取集群UUID映射
        cid_set = {r.cluster_id for r in rows if r.cluster_id is not None}
        uuid_map: dict[int, str] = {}
        if cid_set:
            res = await db.execute(select(Cluster.id, Cluster.uuid).where(Cluster.id.in_(list(cid_set))))
            uuid_map = {rid: str(u) for rid, u in res.all()}

        items = []
        for r in rows:
            meta = {}
            try:
                meta = json.loads(r.message or "{}")
            except Exception:
                meta = {}
            items.append(
                {
                    "id": r.log_id,
                    "type": meta.get("type"),
                    "level": (r.log_level or "").lower(),
                    "status": meta.get("status"),
                    "title": meta.get("title"),
                    "cluster": uuid_map.get(r.cluster_id) or meta.get("cluster"),
                    "node": r.host or meta.get("node"),
                    "created": r.timestamp.isoformat() if r.timestamp else None,
                }
            )
        return {"items": items, "total": int(total)}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


@router.post("/faults")
async def create_fault(req: FaultCreate, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        # 仅 admin/ops 允许新增
        uname = _get_username(user)
        if uname not in {"admin", "ops"}:
            raise HTTPException(status_code=403, detail="not_allowed")
        # 查找集群ID
        cid = None
        if req.cluster:
            cid_res = await db.execute(select(Cluster.id).where(Cluster.uuid == req.cluster).limit(1))
            cid = cid_res.scalars().first()
            if not cid:
                name_res = await db.execute(select(Cluster.id).where(Cluster.name == req.cluster).limit(1))
                cid = name_res.scalars().first()
        ts = _now()
        if req.created:
            try:
                ts = datetime.fromisoformat(req.created.replace("Z", "+00:00"))
            except Exception:
                pass
        meta = {"type": req.type, "status": req.status, "title": req.title, "cluster": req.cluster, "node": req.node}
        log = SystemLog(
            log_id=req.id,
            fault_id=None,
            cluster_id=cid,
            timestamp=ts,
            host=req.node or None,
            service="fault",
            source=uname,
            log_level=_map_level(req.level),
            message=json.dumps(meta, ensure_ascii=False),
            exception=None,
            raw_log=None,
            processed=False,
            created_at=_now(),
        )
        db.add(log)
        await db.flush()
        await db.commit()
        return {"ok": True}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


@router.put("/faults/{fid}")
async def update_fault(fid: str, req: FaultUpdate, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        uname = _get_username(user)
        if uname not in {"admin", "ops"}:
            raise HTTPException(status_code=403, detail="not_allowed")
        res = await db.execute(select(SystemLog).where(SystemLog.log_id == fid, SystemLog.service == "fault").limit(1))
        row = res.scalars().first()
        if not row:
            raise HTTPException(status_code=404, detail="not_found")
        meta = {}
        try:
            meta = json.loads(row.message or "{}")
        except Exception:
            meta = {}
        if req.status is not None:
            meta["status"] = req.status
        if req.title is not None:
            meta["title"] = req.title
        await db.execute(
            update(SystemLog).where(SystemLog.id == row.id).values(message=json.dumps(meta, ensure_ascii=False))
        )
        await db.commit()
        return {"ok": True}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


@router.delete("/faults/{fid}")
async def delete_fault(fid: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        uname = _get_username(user)
        if uname not in {"admin", "ops"}:
            raise HTTPException(status_code=403, detail="not_allowed")
        await db.execute(delete(SystemLog).where(SystemLog.log_id == fid, SystemLog.service == "fault"))
        await db.commit()
        return {"ok": True}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")
