from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, text
from ..db import get_db
from ..models.clusters import Cluster
from ..deps.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid as uuidlib

router = APIRouter()


def _health_to_contract(h: str) -> str:
    if h == "healthy":
        return "running"
    return h or "unknown"


def _health_from_contract(h: str) -> str:
    if h == "running":
        return "healthy"
    return h if h in {"healthy", "warning", "error", "unknown"} else "unknown"


def _pick_primary(ci: dict | None) -> tuple[str | None, str | None]:
    if not isinstance(ci, dict):
        return None, None
    ph = ci.get("primary_host")
    pi = ci.get("primary_ip")
    if ph or pi:
        return ph, pi
    nodes = ci.get("nodes")
    if isinstance(nodes, list) and nodes:
        for n in nodes:
            svcs = n.get("services") or []
            if isinstance(svcs, list) and ("NameNode" in svcs or "ResourceManager" in svcs):
                return n.get("hostname"), n.get("ip")
        return nodes[0].get("hostname"), nodes[0].get("ip")
    return None, None


def _get_username(u) -> str:
    return getattr(u, "username", None) or (u.get("username") if isinstance(u, dict) else None)


class ClusterCreateRequest(BaseModel):
    uuid: str
    host: str
    ip: str
    count: int
    health: str


@router.get("/clusters")
async def list_clusters(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """按当前用户归属返回其可访问的集群列表。"""
    try:
        name = _get_username(user)
        uid_res = await db.execute(text("SELECT id FROM users WHERE username=:un LIMIT 1"), {"un": name})
        uid_row = uid_res.first()
        if not uid_row:
            return {"clusters": []}
        ids_res = await db.execute(text("SELECT cluster_id FROM user_cluster_mapping WHERE user_id=:uid"), {"uid": uid_row[0]})
        cluster_ids = [r[0] for r in ids_res.all()]
        if not cluster_ids:
            return {"clusters": []}
        result = await db.execute(select(Cluster).where(Cluster.id.in_(cluster_ids)))
        rows = result.scalars().all()
        data = []
        for c in rows:
            host, ip = _pick_primary(c.config_info)
            data.append({
                "uuid": str(c.uuid),
                "host": host or c.name,
                "ip": ip or None,
                "count": c.node_count,
                "health": _health_to_contract(c.health_status),
            })
        return {"clusters": data}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


@router.post("/clusters")
async def create_cluster(req: ClusterCreateRequest, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """注册一个集群并建立当前用户的归属映射。"""
    try:
        name = _get_username(user)
        if name not in {"admin", "ops"}:
            raise HTTPException(status_code=403, detail="not_allowed")
        errors: list[dict] = []
        try:
            uuid_obj = uuidlib.UUID(req.uuid)
        except Exception:
            errors.append({"field": "uuid", "message": "UUID 格式不正确"})
            uuid_obj = None
        if not req.host:
            errors.append({"field": "host", "message": "主机名不能为空"})
        if not req.ip:
            errors.append({"field": "ip", "message": "IP 不能为空"})
        if req.count <= 0:
            errors.append({"field": "count", "message": "节点数量必须为正数"})
        if errors:
            raise HTTPException(status_code=400, detail={"errors": errors})
        exists = await db.execute(select(Cluster.id).where(Cluster.uuid == str(uuid_obj)).limit(1))
        if exists.scalars().first():
            raise HTTPException(status_code=409, detail={"errors": [{"field": "uuid", "message": "UUID 已存在"}]})
        c = Cluster(
            uuid=str(uuid_obj),
            name=req.host,
            type="Hadoop",
            node_count=req.count,
            health_status=_health_from_contract(req.health),
            description=None,
            config_info={"primary_host": req.host, "primary_ip": req.ip},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(c)
        await db.flush()
        uid_res = await db.execute(text("SELECT id FROM users WHERE username=:un LIMIT 1"), {"un": name})
        uid_row = uid_res.first()
        role_key = "admin" if name == "admin" else "operator"
        rid_res = await db.execute(text("SELECT id FROM roles WHERE role_key=:rk LIMIT 1"), {"rk": role_key})
        rid_row = rid_res.first()
        if uid_row and rid_row:
            await db.execute(text("INSERT INTO user_cluster_mapping(user_id, cluster_id, role_id) VALUES (:uid,:cid,:rid) ON CONFLICT (user_id, cluster_id) DO NOTHING"), {"uid": uid_row[0], "cid": c.id, "rid": rid_row[0]})
        await db.commit()
        return {"ok": True}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


@router.delete("/clusters/{uuid}")
async def delete_cluster(uuid: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """注销指定集群，并清理用户归属映射。"""
    try:
        name = _get_username(user)
        if name not in {"admin", "ops"}:
            raise HTTPException(status_code=403, detail="not_allowed")
        try:
            uo = uuidlib.UUID(uuid)
        except Exception:
            raise HTTPException(status_code=400, detail={"errors": [{"field": "uuid", "message": "UUID 格式不正确"}]})
        res = await db.execute(select(Cluster).where(Cluster.uuid == str(uo)).limit(1))
        c = res.scalars().first()
        if not c:
            return {"ok": True}
        await db.execute(delete(Cluster).where(Cluster.id == c.id))
        await db.execute(text("DELETE FROM user_cluster_mapping WHERE cluster_id=:cid"), {"cid": c.id})
        await db.commit()
        return {"ok": True}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")
