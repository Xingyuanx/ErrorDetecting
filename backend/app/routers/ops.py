from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import shlex
import uuid as uuidlib
import asyncio

from ..db import get_db
from ..deps.auth import get_current_user, PermissionChecker
from ..models.nodes import Node
from ..models.clusters import Cluster
from ..models.sys_exec_logs import SysExecLog
from ..models.hadoop_exec_logs import HadoopExecLog
from ..services.runner import run_remote_command
from ..ssh_utils import SSHClient
from ..config import now_bj


router = APIRouter()


def _now() -> datetime:
    """返回当前 UTC 时间。"""
    return now_bj()


def _get_username(u) -> str:
    """提取用户名。"""
    return getattr(u, "username", None) or (u.get("username") if isinstance(u, dict) else None) or "system"


def _require_ops(u):
    """校验用户是否具有运维权限。"""
    name = _get_username(u)
    if name not in {"admin", "ops"}:
        raise HTTPException(status_code=403, detail="not_allowed")


async def _find_accessible_node(db: AsyncSession, user_name: str, hostname: str) -> Node | None:
    """在用户可访问的集群中查找指定主机名的节点。"""
    uid_res = await db.execute(text("SELECT id FROM users WHERE username=:un LIMIT 1"), {"un": user_name})
    uid_row = uid_res.first()
    if not uid_row:
        return None
    ids_res = await db.execute(text("SELECT cluster_id FROM user_cluster_mapping WHERE user_id=:uid"), {"uid": uid_row[0]})
    cluster_ids = [r[0] for r in ids_res.all()]
    if not cluster_ids:
        return None
    res = await db.execute(select(Node).where(Node.hostname == hostname, Node.cluster_id.in_(cluster_ids)).limit(1))
    return res.scalars().first()


def _gen_exec_id() -> str:
    """生成执行记录ID。"""
    return uuidlib.uuid4().hex[:32]


class ReadLogReq(BaseModel):
    node: str = Field(..., description="目标节点主机名")
    path: str = Field(..., description="日志文件路径")
    lines: int = Field(200, ge=1, le=5000, description="读取行数")
    pattern: str | None = Field(None, description="可选过滤正则")
    sshUser: str | None = Field(None, description="SSH 用户名（可选）")
    timeout: int = Field(20, ge=1, le=120, description="命令超时时间")








async def _write_exec_log(db: AsyncSession, operation_id: str, description: str, user_id: int):
    """写入系统操作日志。"""
    row = SysExecLog(
        user_id=user_id,
        description=description,
        operation_time=_now()
    )
    db.add(row)
    await db.flush()
    await db.commit()


@router.post("/ops/read-log")
async def read_log(req: ReadLogReq, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """读取远端日志文件内容，支持可选筛选。"""
    try:
        _require_ops(user)
        uname = _get_username(user)
        # 假设这里需要 user_id，从 user 对象获取或查询
        user_id = getattr(user, "id", 1) 
        node = await _find_accessible_node(db, uname, req.node)
        if not node:
            raise HTTPException(status_code=404, detail="node_not_found")
        path_q = shlex.quote(req.path)
        cmd = f"tail -n {req.lines} {path_q}"
        if req.pattern:
            pat_q = shlex.quote(req.pattern)
            cmd = f"{cmd} | grep -E {pat_q}"
        
        start = _now()
        code, out, err = await run_remote_command(str(getattr(node, "ip_address", "")), req.sshUser or "", cmd, timeout=req.timeout)
        
        desc = f"Read log: {req.path} on {req.node} (Exit: {code})"
        await _write_exec_log(db, None, desc, user_id)
        
        if code != 0:
            raise HTTPException(status_code=500, detail="exec_failed")
        lines = [ln for ln in out.splitlines()]
        return {"exitCode": code, "lines": lines}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


async def _write_hadoop_exec_log(db: AsyncSession, user_id: int, cluster_name: str, description: str, start_time: datetime, end_time: datetime):
    """写入 Hadoop 执行审计日志。"""
    row = HadoopExecLog(
        from_user_id=user_id,
        cluster_name=cluster_name,
        description=description,
        start_time=start_time,
        end_time=end_time
    )
    db.add(row)
    await db.flush()
    await db.commit()


@router.post("/ops/clusters/{cluster_uuid}/start")
async def start_cluster(
    cluster_uuid: str, 
    user=Depends(PermissionChecker(["cluster:start"])), 
    db: AsyncSession = Depends(get_db)
):
    """启动集群：在 NameNode 执行 hsfsstart，在 ResourceManager 执行 yarnstart。"""
    try:
        # UUID 格式校验
        try:
            uuidlib.UUID(cluster_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="invalid_uuid_format")

        uname = _get_username(user)
        user_id = getattr(user, "id", 1)

        # 1. 查找集群
        res = await db.execute(select(Cluster).where(Cluster.uuid == cluster_uuid).limit(1))
        cluster = res.scalars().first()
        if not cluster:
            raise HTTPException(status_code=404, detail="cluster_not_found")

        # 2. 获取 SSH 用户 (从关联节点中获取，默认为 hadoop)
        node_res = await db.execute(select(Node).where(Node.cluster_id == cluster.id).limit(1))
        node = node_res.scalars().first()
        ssh_user = node.ssh_user if node and node.ssh_user else "hadoop"

        start_time = _now()
        logs = []

        # 3. 在 NameNode 执行 start-dfs.sh
        if cluster.namenode_ip and cluster.namenode_psw:
            try:
                def run_nn_start():
                    with SSHClient(str(cluster.namenode_ip), ssh_user, cluster.namenode_psw) as client:
                        return client.execute_command("start-dfs.sh")
                out, err = await asyncio.to_thread(run_nn_start)
                logs.append(f"NameNode ({cluster.namenode_ip}) start: {out} {err}")
            except Exception as e:
                logs.append(f"NameNode ({cluster.namenode_ip}) start failed: {str(e)}")
        
        # 4. 在 ResourceManager 执行 start-yarn.sh
        if cluster.rm_ip and cluster.rm_psw:
            try:
                def run_rm_start():
                    with SSHClient(str(cluster.rm_ip), ssh_user, cluster.rm_psw) as client:
                        return client.execute_command("start-yarn.sh")
                out, err = await asyncio.to_thread(run_rm_start)
                logs.append(f"ResourceManager ({cluster.rm_ip}) start: {out} {err}")
            except Exception as e:
                logs.append(f"ResourceManager ({cluster.rm_ip}) start failed: {str(e)}")

        end_time = _now()
        
        # 5. 更新集群状态 (仅当所有尝试都未抛出异常时)
        # 改进：检查是否有失败日志
        has_failed = any("failed" in log.lower() for log in logs)
        if not has_failed:
            cluster.health_status = "healthy"
        else:
            cluster.health_status = "error"
            
        cluster.updated_at = end_time
        await db.flush()

        # 6. 记录日志
        full_desc = " | ".join(logs)
        await _write_hadoop_exec_log(db, user_id, cluster.name, f"Start Cluster: {full_desc}", start_time, end_time)
        
        return {"status": "success", "logs": logs}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error starting cluster: {e}")
        raise HTTPException(status_code=500, detail="server_error")


@router.post("/ops/clusters/{cluster_uuid}/stop")
async def stop_cluster(
    cluster_uuid: str, 
    user=Depends(PermissionChecker(["cluster:stop"])), 
    db: AsyncSession = Depends(get_db)
):
    """停止集群：在 NameNode 执行 hsfsstop，在 ResourceManager 执行 yarnstop。"""
    try:
        # UUID 格式校验
        try:
            uuidlib.UUID(cluster_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="invalid_uuid_format")

        uname = _get_username(user)
        user_id = getattr(user, "id", 1)

        # 1. 查找集群
        res = await db.execute(select(Cluster).where(Cluster.uuid == cluster_uuid).limit(1))
        cluster = res.scalars().first()
        if not cluster:
            raise HTTPException(status_code=404, detail="cluster_not_found")

        # 2. 获取 SSH 用户
        node_res = await db.execute(select(Node).where(Node.cluster_id == cluster.id).limit(1))
        node = node_res.scalars().first()
        ssh_user = node.ssh_user if node and node.ssh_user else "hadoop"

        start_time = _now()
        logs = []

        # 3. 在 NameNode 执行 stop-dfs.sh
        if cluster.namenode_ip and cluster.namenode_psw:
            try:
                def run_nn_stop():
                    with SSHClient(str(cluster.namenode_ip), ssh_user, cluster.namenode_psw) as client:
                        return client.execute_command("stop-dfs.sh")
                out, err = await asyncio.to_thread(run_nn_stop)
                logs.append(f"NameNode ({cluster.namenode_ip}) stop: {out} {err}")
            except Exception as e:
                logs.append(f"NameNode ({cluster.namenode_ip}) stop failed: {str(e)}")
        
        # 4. 在 ResourceManager 执行 stop-yarn.sh
        if cluster.rm_ip and cluster.rm_psw:
            try:
                def run_rm_stop():
                    with SSHClient(str(cluster.rm_ip), ssh_user, cluster.rm_psw) as client:
                        return client.execute_command("stop-yarn.sh")
                out, err = await asyncio.to_thread(run_rm_stop)
                logs.append(f"ResourceManager ({cluster.rm_ip}) stop: {out} {err}")
            except Exception as e:
                logs.append(f"ResourceManager ({cluster.rm_ip}) stop failed: {str(e)}")

        end_time = _now()
        
        # 5. 更新集群状态
        cluster.health_status = "unknown"
        cluster.updated_at = end_time
        await db.flush()

        # 6. 记录日志
        full_desc = " | ".join(logs)
        await _write_hadoop_exec_log(db, user_id, cluster.name, f"Stop Cluster: {full_desc}", start_time, end_time)
        
        return {"status": "success", "logs": logs}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error stopping cluster: {e}")
        raise HTTPException(status_code=500, detail="server_error")






