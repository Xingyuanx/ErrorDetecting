from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, text
from ..db import get_db
from ..deps.auth import get_current_user
from ..models.nodes import Node
from ..models.clusters import Cluster
from pydantic import BaseModel
from datetime import datetime, timezone

router = APIRouter()


def _get_username(u) -> str:
    return getattr(u, "username", None) or (u.get("username") if isinstance(u, dict) else None)


def _status_to_contract(s: str) -> str:
    if s == "healthy":
        return "running"
    if s == "unhealthy":
        return "stopped"
    return s or "unknown"


def _fmt_percent(v: float | None) -> str:
    if v is None:
        return "-"
    return f"{int(round(v))}%"


def _fmt_updated(ts: datetime | None) -> str:
    if not ts:
        return "-"
    now = datetime.now(timezone.utc)
    diff = int((now - ts).total_seconds())
    if diff < 60:
        return "刚刚"
    if diff < 3600:
        return f"{diff // 60}分钟前"
    return f"{diff // 3600}小时前"


class NodeDetail(BaseModel):
    name: str
    metrics: dict


@router.get("/nodes")
async def list_nodes(cluster: str = Query(...), user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """拉取指定集群的节点列表。"""
    try:
        name = _get_username(user)
        uid_res = await db.execute(text("SELECT id FROM users WHERE username=:un LIMIT 1"), {"un": name})
        uid_row = uid_res.first()
        if not uid_row:
            return {"nodes": []}
        cid_res = await db.execute(select(Cluster.id).where(Cluster.uuid == cluster).limit(1))
        cid = cid_res.scalars().first()
        if not cid:
            return {"nodes": []}
        auth_res = await db.execute(text("SELECT 1 FROM user_cluster_mapping WHERE user_id=:uid AND cluster_id=:cid LIMIT 1"), {"uid": uid_row[0], "cid": cid})
        if not auth_res.first():
            raise HTTPException(status_code=403, detail="not_allowed")
        result = await db.execute(select(Node).where(Node.cluster_id == cid).limit(500))
        rows = result.scalars().all()
        data = [
            {
                "name": n.hostname,
                "ip": str(getattr(n, "ip_address", "")) if getattr(n, "ip_address", None) else None,
                "status": _status_to_contract(n.status),
                "cpu": _fmt_percent(n.cpu_usage),
                "mem": _fmt_percent(n.memory_usage),
                "updated": _fmt_updated(n.last_heartbeat),
            }
            for n in rows
        ]
        return {"nodes": data}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


@router.get("/nodes/{name}")
async def node_detail(name: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """查询节点详情。"""
    try:
        name_u = _get_username(user)
        uid_res = await db.execute(text("SELECT id FROM users WHERE username=:un LIMIT 1"), {"un": name_u})
        uid_row = uid_res.first()
        if not uid_row:
            raise HTTPException(status_code=404, detail="not_found")
        # 仅返回用户可访问集群中的该节点
        ids_res = await db.execute(text("SELECT cluster_id FROM user_cluster_mapping WHERE user_id=:uid"), {"uid": uid_row[0]})
        cluster_ids = [r[0] for r in ids_res.all()]
        if not cluster_ids:
            raise HTTPException(status_code=404, detail="not_found")
        res = await db.execute(select(Node).where(Node.hostname == name, Node.cluster_id.in_(cluster_ids)).limit(1))
        n = res.scalars().first()
        if not n:
            raise HTTPException(status_code=404, detail="not_found")
        return NodeDetail(
            name=n.hostname,
            metrics={
                "cpu": _fmt_percent(n.cpu_usage),
                "mem": _fmt_percent(n.memory_usage),
                "disk": _fmt_percent(n.disk_usage),
                "status": _status_to_contract(n.status),
                "ip": str(getattr(n, "ip_address", "")) if getattr(n, "ip_address", None) else None,
                "lastHeartbeat": getattr(n, "last_heartbeat", None).isoformat() if getattr(n, "last_heartbeat", None) else None,
            },
        ).model_dump()
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


def _require_ops(name: str):
    if name not in {"admin", "ops"}:
        raise HTTPException(status_code=403, detail="not_allowed")


async def _find_accessible_node(db: AsyncSession, user_id: int, hostname: str) -> Node | None:
    ids_res = await db.execute(text("SELECT cluster_id FROM user_cluster_mapping WHERE user_id=:uid"), {"uid": user_id})
    cluster_ids = [r[0] for r in ids_res.all()]
    if not cluster_ids:
        return None
    res = await db.execute(select(Node).where(Node.hostname == hostname, Node.cluster_id.in_(cluster_ids)).limit(1))
    return res.scalars().first()


@router.post("/nodes/{name}/start")
async def start_node(name: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """启动节点：状态设为 healthy。"""
    try:
        uname = _get_username(user)
        _require_ops(uname)
        uid_res = await db.execute(text("SELECT id FROM users WHERE username=:un LIMIT 1"), {"un": uname})
        uid_row = uid_res.first()
        if not uid_row:
            raise HTTPException(status_code=404, detail="not_found")
        n = await _find_accessible_node(db, uid_row[0], name)
        if not n:
            raise HTTPException(status_code=404, detail="not_found")
        await db.execute(update(Node).where(Node.id == n.id).values(status="healthy", last_heartbeat=func.now(), updated_at=func.now()))
        await db.commit()
        return {"ok": True}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


@router.post("/nodes/{name}/stop")
async def stop_node(name: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """停止节点：状态设为 unhealthy。"""
    try:
        uname = _get_username(user)
        _require_ops(uname)
        uid_res = await db.execute(text("SELECT id FROM users WHERE username=:un LIMIT 1"), {"un": uname})
        uid_row = uid_res.first()
        if not uid_row:
            raise HTTPException(status_code=404, detail="not_found")
        n = await _find_accessible_node(db, uid_row[0], name)
        if not n:
            raise HTTPException(status_code=404, detail="not_found")
        await db.execute(update(Node).where(Node.id == n.id).values(status="unhealthy", updated_at=func.now()))
        await db.commit()
        return {"ok": True}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


@router.delete("/nodes/{name}")
async def delete_node(name: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """删除节点。"""
    try:
        uname = _get_username(user)
        _require_ops(uname)
        uid_res = await db.execute(text("SELECT id FROM users WHERE username=:un LIMIT 1"), {"un": uname})
        uid_row = uid_res.first()
        if not uid_row:
            return {"ok": True}
        n = await _find_accessible_node(db, uid_row[0], name)
        if not n:
            return {"ok": True}
        await db.execute(delete(Node).where(Node.id == n.id))
        await db.commit()
        return {"ok": True}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")
