from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, text
from ..db import get_db
from ..models.clusters import Cluster
from ..models.nodes import Node
from ..deps.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid as uuidlib

router = APIRouter()


def _get_username(u) -> str:
    return getattr(u, "username", None) or (u.get("username") if isinstance(u, dict) else None)


class NodeCreateItem(BaseModel):
    hostname: str
    ip_address: str
    ssh_user: str
    ssh_password: str
    description: str | None = None

class ClusterCreateRequest(BaseModel):
    name: str
    type: str
    node_count: int
    health_status: str
    namenode_ip: str | None = None
    namenode_psw: str | None = None
    rm_ip: str | None = None
    rm_psw: str | None = None
    nodes: list[NodeCreateItem]


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
            data.append({
                "uuid": str(c.uuid),
                "name": c.name,
                "type": c.type,
                "node_count": c.node_count,
                "health_status": c.health_status,
                "namenode_ip": c.namenode_ip,
                "namenode_psw": c.namenode_psw,
                "rm_ip": c.rm_ip,
                "rm_psw": c.rm_psw,
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
        
        # 检查集群名称是否已存在
        exists = await db.execute(select(Cluster.id).where(Cluster.name == req.name).limit(1))
        if exists.scalars().first():
             # 使用指南建议的错误格式
            raise HTTPException(status_code=400, detail={"errors": [{"field": "name", "message": "集群名称已存在"}]})

        new_uuid = str(uuidlib.uuid4())
        
        c = Cluster(
            uuid=new_uuid,
            name=req.name,
            type=req.type,
            node_count=req.node_count,
            health_status=req.health_status,
            namenode_ip=req.namenode_ip,
            namenode_psw=req.namenode_psw,
            rm_ip=req.rm_ip,
            rm_psw=req.rm_psw,
            description=None,
            config_info={}, # 保留为空字典或根据需要填充
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(c)
        await db.flush() # 获取 c.id

        # 插入节点
        for n_req in req.nodes:
            node_uuid = str(uuidlib.uuid4())
            node = Node(
                uuid=node_uuid,
                cluster_id=c.id,
                hostname=n_req.hostname,
                ip_address=n_req.ip_address,
                ssh_user=n_req.ssh_user,
                ssh_password=n_req.ssh_password,
                description=n_req.description,
                status="unknown",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(node)

        # 建立用户映射
        uid_res = await db.execute(text("SELECT id FROM users WHERE username=:un LIMIT 1"), {"un": name})
        uid_row = uid_res.first()
        role_key = "admin" if name == "admin" else "operator"
        rid_res = await db.execute(text("SELECT id FROM roles WHERE role_key=:rk LIMIT 1"), {"rk": role_key})
        rid_row = rid_res.first()
        if uid_row and rid_row:
            await db.execute(text("INSERT INTO user_cluster_mapping(user_id, cluster_id, role_id) VALUES (:uid,:cid,:rid) ON CONFLICT (user_id, cluster_id) DO NOTHING"), {"uid": uid_row[0], "cid": c.id, "rid": rid_row[0]})
        
        await db.commit()
        
        return {
            "status": "success",
            "message": "集群注册成功",
            "uuid": new_uuid
        }
    except HTTPException:
        raise
    except Exception as e:
        # 这里可以记录日志
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
