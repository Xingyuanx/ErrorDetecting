from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, update
from ..db import get_db
from ..models.hadoop_logs import HadoopLog
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
    id: str | None = None
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
        stmt = select(HadoopLog).where(HadoopLog.title == "fault")
        count_stmt = select(func.count(HadoopLog.log_id)).where(HadoopLog.title == "fault")

        if cluster:
            stmt = stmt.where(HadoopLog.cluster_name == cluster)
            count_stmt = count_stmt.where(HadoopLog.cluster_name == cluster)
        if node:
            stmt = stmt.where(HadoopLog.node_host == node)
            count_stmt = count_stmt.where(HadoopLog.node_host == node)
        if time_from:
            try:
                tf = datetime.fromisoformat(time_from.replace("Z", "+00:00"))
                stmt = stmt.where(HadoopLog.log_time >= tf)
                count_stmt = count_stmt.where(HadoopLog.log_time >= tf)
            except Exception:
                pass

        stmt = stmt.order_by(HadoopLog.log_time.desc()).offset((page - 1) * size).limit(size)
        rows = (await db.execute(stmt)).scalars().all()
        total = (await db.execute(count_stmt)).scalar() or 0

        items = []
        for r in rows:
            meta = {}
            try:
                if r.info:
                    meta = json.loads(r.info)
            except Exception:
                pass
            
            items.append({
                "id": str(r.log_id),
                "type": meta.get("type", "unknown"),
                "level": r.title,
                "status": meta.get("status", "active"),
                "title": meta.get("title", r.title),
                "cluster": r.cluster_name,
                "node": r.node_host,
                "created": r.log_time.isoformat() if r.log_time else None
            })
        return {"items": items, "total": int(total)}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error listing faults: {e}")
        raise HTTPException(status_code=500, detail="server_error")


@router.post("/faults")
async def create_fault(req: FaultCreate, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        uname = _get_username(user)
        if uname not in {"admin", "ops"}:
            raise HTTPException(status_code=403, detail="not_allowed")
        
        # 确定集群名称
        cluster_name = req.cluster or "unknown"
        if req.cluster and "-" in req.cluster: # 可能是 UUID
             res = await db.execute(select(Cluster.name).where(Cluster.uuid == req.cluster).limit(1))
             name = res.scalars().first()
             if name:
                 cluster_name = name

        ts = _now()
        if req.created:
            try:
                ts = datetime.fromisoformat(req.created.replace("Z", "+00:00"))
            except Exception:
                pass

        meta = {"type": req.type, "status": req.status, "title": req.title, "cluster": req.cluster, "node": req.node}
        log = HadoopLog(
            cluster_name=cluster_name,
            node_host=req.node or "unknown",
            title="fault",
            info=json.dumps(meta, ensure_ascii=False),
            log_time=ts
        )
        db.add(log)
        await db.commit()
        return {"ok": True, "id": log.log_id}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating fault: {e}")
        raise HTTPException(status_code=500, detail="server_error")


@router.put("/faults/{fid}")
async def update_fault(fid: int, req: FaultUpdate, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        uname = _get_username(user)
        if uname not in {"admin", "ops"}:
            raise HTTPException(status_code=403, detail="not_allowed")
        
        res = await db.execute(select(HadoopLog).where(HadoopLog.log_id == fid, HadoopLog.title == "fault").limit(1))
        row = res.scalars().first()
        if not row:
            raise HTTPException(status_code=404, detail="not_found")
        
        meta = {}
        try:
            if row.info:
                meta = json.loads(row.info)
        except Exception:
            pass
            
        if req.status is not None:
            meta["status"] = req.status
        if req.title is not None:
            meta["title"] = req.title
            
        row.info = json.dumps(meta, ensure_ascii=False)
        await db.commit()
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating fault: {e}")
        raise HTTPException(status_code=500, detail="server_error")


@router.delete("/faults/{fid}")
async def delete_fault(fid: int, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        uname = _get_username(user)
        if uname not in {"admin", "ops"}:
            raise HTTPException(status_code=403, detail="not_allowed")
        await db.execute(delete(HadoopLog).where(HadoopLog.log_id == fid, HadoopLog.title == "fault"))
        await db.commit()
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting fault: {e}")
        raise HTTPException(status_code=500, detail="server_error")
