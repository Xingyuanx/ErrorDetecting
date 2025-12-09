import shlex
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from ..models.nodes import Node
from ..models.exec_logs import ExecLog
from .runner import run_remote_command


def _now() -> datetime:
    """返回当前 UTC 时间。"""
    return datetime.now(timezone.utc)


async def _find_accessible_node(db: AsyncSession, user_name: str, hostname: str) -> Optional[Node]:
    """校验用户对节点的访问权限，并返回节点对象。"""
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


async def _write_exec_log(db: AsyncSession, exec_id: str, command_type: str, status: str, start: datetime, end: Optional[datetime], exit_code: Optional[int], operator: str, stdout: Optional[str] = None, stderr: Optional[str] = None):
    """写入执行审计日志。"""
    row = ExecLog(
        exec_id=exec_id,
        fault_id="-",
        command_type=command_type,
        script_path=None,
        command_content="[tool]",
        target_nodes=None,
        risk_level="medium",
        execution_status=status,
        start_time=start,
        end_time=end,
        duration=(int((end - start).total_seconds()) if (start and end) else None),
        stdout_log=stdout,
        stderr_log=stderr,
        exit_code=exit_code,
        operator=operator,
        created_at=_now(),
        updated_at=_now(),
    )
    db.add(row)
    await db.flush()
    await db.commit()


async def tool_read_log(db: AsyncSession, user_name: str, node: str, path: str, lines: int = 200, pattern: Optional[str] = None, ssh_user: Optional[str] = None, timeout: int = 20) -> Dict[str, Any]:
    """工具：读取远端日志并可选筛选。"""
    n = await _find_accessible_node(db, user_name, node)
    if not n:
        return {"error": "node_not_found"}
    path_q = shlex.quote(path)
    cmd = f"tail -n {lines} {path_q}"
    if pattern:
        pat_q = shlex.quote(pattern)
        cmd = f"{cmd} | grep -E {pat_q}"
    start = _now()
    code, out, err = await run_remote_command(str(getattr(n, "ip_address", "")), ssh_user or "", cmd, timeout=timeout)
    end = _now()
    exec_id = f"tool_{start.timestamp():.0f}"
    await _write_exec_log(db, exec_id, "read_log", ("success" if code == 0 else "failed"), start, end, code, user_name, out, err)
    return {"execId": exec_id, "exitCode": code, "stdout": out, "stderr": err}


async def tool_kill_process(db: AsyncSession, user_name: str, node: str, pid: int, signal: int = 9, ssh_user: Optional[str] = None, timeout: int = 15) -> Dict[str, Any]:
    """工具：远端 kill 进程。"""
    n = await _find_accessible_node(db, user_name, node)
    if not n:
        return {"error": "node_not_found"}
    start = _now()
    cmd = f"kill -{signal} {pid}"
    code, out, err = await run_remote_command(str(getattr(n, "ip_address", "")), ssh_user or "", cmd, timeout=timeout)
    end = _now()
    exec_id = f"tool_{start.timestamp():.0f}"
    await _write_exec_log(db, exec_id, "kill", ("success" if code == 0 else "failed"), start, end, code, user_name, out, err)
    return {"execId": exec_id, "exitCode": code, "stdout": out, "stderr": err}


async def tool_reboot_node(db: AsyncSession, user_name: str, node: str, ssh_user: Optional[str] = None, timeout: int = 20) -> Dict[str, Any]:
    """工具：远端重启节点。"""
    n = await _find_accessible_node(db, user_name, node)
    if not n:
        return {"error": "node_not_found"}
    start = _now()
    cmd = "sudo -n /sbin/reboot || sudo -n reboot || /sbin/reboot || reboot"
    code, out, err = await run_remote_command(str(getattr(n, "ip_address", "")), ssh_user or "", cmd, timeout=timeout)
    end = _now()
    exec_id = f"tool_{start.timestamp():.0f}"
    await _write_exec_log(db, exec_id, "reboot", ("success" if code == 0 else "failed"), start, end, code, user_name, out, err)
    return {"execId": exec_id, "exitCode": code, "stdout": out, "stderr": err}


def openai_tools_schema() -> List[Dict[str, Any]]:
    """返回 OpenAI 兼容的工具定义（Function Calling）。"""
    return [
        {
            "type": "function",
            "function": {
                "name": "read_log",
                "description": "读取指定节点的日志文件并可按正则筛选",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "node": {"type": "string"},
                        "path": {"type": "string"},
                        "lines": {"type": "integer", "default": 200},
                        "pattern": {"type": "string"},
                        "sshUser": {"type": "string"},
                    },
                    "required": ["node", "path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "kill_process",
                "description": "在远端节点上按 PID 发送信号 kill 进程",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "node": {"type": "string"},
                        "pid": {"type": "integer"},
                        "signal": {"type": "integer", "default": 9},
                        "sshUser": {"type": "string"},
                    },
                    "required": ["node", "pid"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "reboot_node",
                "description": "在远端节点上执行系统重启",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "node": {"type": "string"},
                        "sshUser": {"type": "string"},
                    },
                    "required": ["node"],
                },
            },
        },
    ]

