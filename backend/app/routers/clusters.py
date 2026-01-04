from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, text
from ..db import get_db
from ..models.clusters import Cluster
from ..models.nodes import Node
from ..deps.auth import get_current_user, PermissionChecker
from ..services.ssh_probe import check_ssh_connectivity, get_hdfs_cluster_id
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
    cpu_avg: float | None = None
    memory_avg: float | None = None
    description: str | None = None
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
                "cpu_avg": c.cpu_avg,
                "memory_avg": c.memory_avg,
                "namenode_ip": (str(c.namenode_ip) if c.namenode_ip else None),
                "namenode_psw": c.namenode_psw,
                "rm_ip": (str(c.rm_ip) if c.rm_ip else None),
                "rm_psw": c.rm_psw,
                "description": c.description,
            })
        return {"clusters": data}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


@router.post("/clusters")
async def create_cluster(
    req: ClusterCreateRequest, 
    user=Depends(PermissionChecker(["cluster:register"])), 
    db: AsyncSession = Depends(get_db)
):
    """注册一个集群并建立当前用户的归属映射。"""
    try:
        name = _get_username(user)
        # 移除硬编码的角色检查，PermissionChecker 已经处理了权限校验
        
        # 参数校验：类型与状态
        valid_types = {"hadoop", "spark", "kubernetes"}
        valid_health = {"healthy", "warning", "error", "unknown"}
        errors: list[dict] = []
        if req.type not in valid_types:
            errors.append({"field": "type", "message": "类型不合法，应为 hadoop/spark/kubernetes", "step": "参数校验"})
        if req.health_status not in valid_health:
            errors.append({"field": "health_status", "message": "状态不合法，应为 healthy/warning/error/unknown", "step": "参数校验"})
        if req.node_count is None or req.node_count < 0:
            errors.append({"field": "node_count", "message": "节点总数必须为非负整数", "step": "参数校验"})
        if errors:
            raise HTTPException(status_code=400, detail={"errors": errors})
        
        # 1. 获取 HDFS 集群真实 UUID (从 NameNode 获取)
        cluster_uuid, err = get_hdfs_cluster_id(str(req.namenode_ip), req.nodes[0].ssh_user, req.nodes[0].ssh_password)
        if not cluster_uuid:
            raise HTTPException(status_code=400, detail={"errors": [{"field": "namenode_ip", "message": f"无法获取集群ID: {err}"}]})

        # 2. 检查该 UUID 是否已在数据库中
        res = await db.execute(select(Cluster).where(Cluster.uuid == cluster_uuid).limit(1))
        existing_cluster = res.scalars().first()

        if existing_cluster:
            # 集群已存在，仅建立用户映射
            c = existing_cluster
            new_uuid = cluster_uuid
        else:
            # 集群不存在，执行注册流程
            # 检查集群名称是否已存在
            name_exists = await db.execute(select(Cluster.id).where(Cluster.name == req.name).limit(1))
            if name_exists.scalars().first():
                raise HTTPException(status_code=400, detail={"errors": [{"field": "name", "message": "集群名称已存在"}]})

            # SSH 连通性预检查
            ssh_errors: list[dict] = []
            for idx, n_req in enumerate(req.nodes):
                ip = getattr(n_req, "ip_address", None) or getattr(n_req, "ip", None)
                user_ = getattr(n_req, "ssh_user", None)
                pwd_ = getattr(n_req, "ssh_password", None)
                ok, conn_err = check_ssh_connectivity(str(ip), str(user_ or ""), str(pwd_ or ""))
                if not ok:
                    ssh_errors.append({
                        "field": f"nodes[{idx}].ssh",
                        "message": "注册失败：SSH不可连接",
                        "step": "connect",
                        "detail": conn_err,
                        "hostname": getattr(n_req, "hostname", None),
                        "ip": str(ip) if ip is not None else None,
                    })
            if ssh_errors:
                raise HTTPException(status_code=400, detail={"errors": ssh_errors})
            
            new_uuid = cluster_uuid
            
            c = Cluster(
                uuid=new_uuid,
                name=req.name,
                type=req.type,
                node_count=req.node_count,
                health_status=req.health_status,
                cpu_avg=req.cpu_avg,
                memory_avg=req.memory_avg,
                namenode_ip=req.namenode_ip,
                namenode_psw=req.namenode_psw,
                rm_ip=req.rm_ip,
                rm_psw=req.rm_psw,
                description=req.description,
                config_info={}, 
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
                    status="unknown",
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                db.add(node)

        # 3. 建立用户映射 (无论集群是新注册还是已存在)
        uid_res = await db.execute(text("SELECT id FROM users WHERE username=:un LIMIT 1"), {"un": name})
        uid_row = uid_res.first()
        # 简化逻辑：如果是 admin 用户则赋予 admin 角色，否则赋予 operator 角色
        role_key = "admin" if name == "admin" else "operator"
        rid_res = await db.execute(text("SELECT id FROM roles WHERE role_key=:rk LIMIT 1"), {"rk": role_key})
        rid_row = rid_res.first()
        
        if uid_row and rid_row:
            await db.execute(
                text("INSERT INTO user_cluster_mapping(user_id, cluster_id, role_id) VALUES (:uid,:cid,:rid) ON CONFLICT (user_id, cluster_id) DO NOTHING"), 
                {"uid": uid_row[0], "cid": c.id, "rid": rid_row[0]}
            )
        
        await db.commit()
        
        return {
            "status": "success",
            "message": "集群注册成功" if not existing_cluster else "集群已关联至当前用户",
            "uuid": new_uuid
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="server_error")


@router.delete("/clusters/{uuid}")
async def delete_cluster(
    uuid: str, 
    user=Depends(PermissionChecker(["cluster:delete"])), 
    db: AsyncSession = Depends(get_db)
):
    """注销指定集群，并清理用户归属映射。"""
    try:
        name = _get_username(user)
        # 移除硬编码的角色检查
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
