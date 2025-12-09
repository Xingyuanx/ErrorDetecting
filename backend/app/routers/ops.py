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
from ..models.exec_logs import ExecLog
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


class KillReq(BaseModel):
    node: str = Field(..., description="目标节点主机名")
    pid: int = Field(..., ge=2, description="进程 PID")
    signal: int = Field(9, ge=1, le=31, description="信号编号，默认 9")
    sshUser: str | None = Field(None, description="SSH 用户名（可选）")
    timeout: int = Field(15, ge=1, le=60, description="命令超时时间")


class RebootReq(BaseModel):
    node: str = Field(..., description="目标节点主机名")
    sshUser: str | None = Field(None, description="SSH 用户名（可选）")
    timeout: int = Field(20, ge=1, le=120, description="命令超时时间")


async def _write_exec_log(db: AsyncSession, exec_id: str, command_type: str, status: str, start: datetime, end: datetime | None, exit_code: int | None, operator: str):
    """写入或更新执行审计日志。"""
    row = ExecLog(
        exec_id=exec_id,
        fault_id="-",
        command_type=command_type,
        script_path=None,
        command_content="[api]",
        target_nodes=None,
        risk_level="medium",
        execution_status=status,
        start_time=start,
        end_time=end,
        duration=(int((end - start).total_seconds()) if (start and end) else None),
        stdout_log=None,
        stderr_log=None,
        exit_code=exit_code,
        operator=operator,
        created_at=_now(),
        updated_at=_now(),
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
        node = await _find_accessible_node(db, uname, req.node)
        if not node:
            raise HTTPException(status_code=404, detail="node_not_found")
        path_q = shlex.quote(req.path)
        cmd = f"tail -n {req.lines} {path_q}"
        if req.pattern:
            pat_q = shlex.quote(req.pattern)
            cmd = f"{cmd} | grep -E {pat_q}"
        exec_id = _gen_exec_id()
        start = _now()
        code, out, err = await run_remote_command(str(getattr(node, "ip_address", "")), req.sshUser or "", cmd, timeout=req.timeout)
        end = _now()
        await _write_exec_log(db, exec_id, "read_log", ("success" if code == 0 else "failed"), start, end, code, uname)
        if code != 0:
            raise HTTPException(status_code=500, detail="exec_failed")
        lines = [ln for ln in out.splitlines()]
        return {"execId": exec_id, "exitCode": code, "lines": lines}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


@router.post("/ops/kill")
async def kill_process(req: KillReq, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """在远端节点执行 kill 操作。"""
    try:
        _require_ops(user)
        uname = _get_username(user)
        node = await _find_accessible_node(db, uname, req.node)
        if not node:
            raise HTTPException(status_code=404, detail="node_not_found")
        exec_id = _gen_exec_id()
        start = _now()
        cmd = f"kill -{req.signal} {req.pid}"
        code, out, err = await run_remote_command(str(getattr(node, "ip_address", "")), req.sshUser or "", cmd, timeout=req.timeout)
        end = _now()
        await _write_exec_log(db, exec_id, "kill", ("success" if code == 0 else "failed"), start, end, code, uname)
        if code != 0:
            raise HTTPException(status_code=500, detail="exec_failed")
        return {"execId": exec_id, "exitCode": code}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


@router.post("/ops/reboot")
async def reboot_node(req: RebootReq, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """在远端节点执行 reboot 操作。"""
    try:
        _require_ops(user)
        uname = _get_username(user)
        node = await _find_accessible_node(db, uname, req.node)
        if not node:
            raise HTTPException(status_code=404, detail="node_not_found")
        exec_id = _gen_exec_id()
        start = _now()
        cmd = "sudo -n /sbin/reboot || sudo -n reboot || /sbin/reboot || reboot"
        code, out, err = await run_remote_command(str(getattr(node, "ip_address", "")), req.sshUser or "", cmd, timeout=req.timeout)
        end = _now()
        await _write_exec_log(db, exec_id, "reboot", ("success" if code == 0 else "failed"), start, end, code, uname)
        if code != 0:
            raise HTTPException(status_code=500, detail="exec_failed")
        return {"execId": exec_id, "exitCode": code}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")

