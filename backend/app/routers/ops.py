from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import shlex
import uuid as uuidlib

from ..db import get_db
from ..deps.auth import get_current_user
from ..models.nodes import Node
from ..models.sys_exec_logs import SysExecLog
from ..services.runner import run_remote_command


router = APIRouter()


def _now() -> datetime:
    """返回当前 UTC 时间。"""
    return datetime.now(timezone.utc)


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







