from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from ..db import get_db
from ..models.hadoop_exec_logs import HadoopExecLog
from ..deps.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime, timezone

router = APIRouter()


class ExecLogCreate(BaseModel):
    from_user_id: int
    cluster_name: str
    description: str | None = None
    start_time: str | None = None
    end_time: str | None = None


class ExecLogUpdate(BaseModel):
    description: str | None = None
    start_time: str | None = None
    end_time: str | None = None


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
        result = await db.execute(select(HadoopExecLog).order_by(HadoopExecLog.start_time.desc()))
        rows = result.scalars().all()
        return {"items": [r.to_dict() for r in rows]}
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


@router.post("/exec-logs")
async def create_exec_log(req: ExecLogCreate, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        st = _parse_time(req.start_time)
        et = _parse_time(req.end_time)
        
        row = HadoopExecLog(
            from_user_id=req.from_user_id,
            cluster_name=req.cluster_name,
            description=req.description,
            start_time=st,
            end_time=et
        )
        db.add(row)
        await db.flush()
        await db.commit()
        return {"ok": True, "id": row.id}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating exec log: {e}")
        raise HTTPException(status_code=500, detail="server_error")


@router.put("/exec-logs/{log_id}")
async def update_exec_log(log_id: int, req: ExecLogUpdate, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        st = _parse_time(req.start_time)
        et = _parse_time(req.end_time)
        values: dict = {}
        if req.description is not None:
            values["description"] = req.description
        if st is not None:
            values["start_time"] = st
        if et is not None:
            values["end_time"] = et
            
        if not values:
             return {"ok": True}

        await db.execute(update(HadoopExecLog).where(HadoopExecLog.id == log_id).values(**values))
        await db.commit()
        return {"ok": True}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


@router.delete("/exec-logs/{log_id}")
async def delete_exec_log(log_id: int, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(delete(HadoopExecLog).where(HadoopExecLog.id == log_id))
        await db.commit()
        return {"ok": True}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")
