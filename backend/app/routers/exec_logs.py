from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from ..db import get_db
from ..models.exec_logs import ExecLog
from ..deps.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime, timezone

router = APIRouter()


class ExecLogCreate(BaseModel):
    exec_id: str
    fault_id: str
    command_type: str
    execution_status: str
    start_time: str | None = None
    end_time: str | None = None
    exit_code: int | None = None


class ExecLogUpdate(BaseModel):
    fault_id: str | None = None
    command_type: str | None = None
    execution_status: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    exit_code: int | None = None


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_time(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)
    except Exception:
        return None


@router.get("/exec-logs")
async def list_exec_logs(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(ExecLog).order_by(ExecLog.start_time.desc()))
        rows = result.scalars().all()
        return {"items": [r.to_dict() for r in rows]}
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


@router.post("/exec-logs")
async def create_exec_log(req: ExecLogCreate, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        st = _parse_time(req.start_time)
        et = _parse_time(req.end_time)
        duration = None
        if st and et:
            duration = int((et - st).total_seconds())
            if duration < 0:
                duration = None
        row = ExecLog(
            exec_id=req.exec_id,
            fault_id=req.fault_id,
            command_type=req.command_type,
            script_path=None,
            command_content="[auto]",
            target_nodes=None,
            risk_level="medium",
            execution_status=req.execution_status,
            start_time=st,
            end_time=et,
            duration=duration,
            stdout_log=None,
            stderr_log=None,
            exit_code=req.exit_code,
            operator=getattr(user, "username", None) or (user.get("username") if isinstance(user, dict) else "system"),
            created_at=_now(),
            updated_at=_now(),
        )
        db.add(row)
        await db.flush()
        await db.commit()
        return {"ok": True}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


@router.put("/exec-logs/{exec_id}")
async def update_exec_log(exec_id: str, req: ExecLogUpdate, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        st = _parse_time(req.start_time)
        et = _parse_time(req.end_time)
        values: dict = {"updated_at": _now()}
        if req.fault_id is not None:
            values["fault_id"] = req.fault_id
        if req.command_type is not None:
            values["command_type"] = req.command_type
        if req.execution_status is not None:
            values["execution_status"] = req.execution_status
        if req.exit_code is not None:
            values["exit_code"] = req.exit_code
        if st is not None:
            values["start_time"] = st
        if et is not None:
            values["end_time"] = et
        if st is not None and et is not None:
            d = int((et - st).total_seconds())
            if d >= 0:
                values["duration"] = d
        res = await db.execute(update(ExecLog).where(ExecLog.exec_id == exec_id).values(**values))
        await db.commit()
        return {"ok": True}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


@router.delete("/exec-logs/{exec_id}")
async def delete_exec_log(exec_id: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(delete(ExecLog).where(ExecLog.exec_id == exec_id))
        await db.commit()
        return {"ok": True}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")

