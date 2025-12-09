import asyncio
import os
import shlex
from typing import Optional, Tuple


async def run_local_command(cmd: str, timeout: int = 30) -> Tuple[int, str, str]:
    """运行本地命令，返回 (exit_code, stdout, stderr)。"""
    if os.name == "nt":
        prog = ["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd]
    else:
        prog = ["bash", "-lc", cmd]
    proc = await asyncio.create_subprocess_exec(
        *prog,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        try:
            proc.kill()
        except Exception:
            pass
        return (124, "", "timeout")
    return (proc.returncode or 0, out.decode(errors="ignore"), err.decode(errors="ignore"))


def _build_ssh_prog(host: str, user: str, cmd: str, port: Optional[int] = None, identity_file: Optional[str] = None) -> list:
    """构造 ssh 远程执行命令参数数组。"""
    prog = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=no",
    ]
    if port:
        prog += ["-p", str(port)]
    if identity_file:
        prog += ["-i", identity_file]
    target = f"{user}@{host}" if user else host
    prog += [target, "bash", "-lc", cmd]
    return prog


async def run_remote_command(host: str, user: str, cmd: str, timeout: int = 30, port: Optional[int] = None, identity_file: Optional[str] = None) -> Tuple[int, str, str]:
    """通过 ssh 在远端主机执行命令，返回 (exit_code, stdout, stderr)。"""
    prog = _build_ssh_prog(host, user, cmd, port=port, identity_file=identity_file)
    proc = await asyncio.create_subprocess_exec(
        *prog,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        try:
            proc.kill()
        except Exception:
            pass
        return (124, "", "timeout")
    return (proc.returncode or 0, out.decode(errors="ignore"), err.decode(errors="ignore"))

