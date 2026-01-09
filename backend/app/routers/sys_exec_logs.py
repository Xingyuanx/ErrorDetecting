from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from ..db import get_db
from ..models.sys_exec_logs import SysExecLog
from ..deps.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class SysExecLogCreate(BaseModel):
    user_id: int
    description: str

@router.get("/sys-exec-logs")
async def list_sys_exec_logs(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
):
    try:
        stmt = select(SysExecLog).order_by(SysExecLog.operation_time.desc()).offset((page - 1) * size).limit(size)
        count_stmt = select(func.count(SysExecLog.operation_id))
        
        rows = (await db.execute(stmt)).scalars().all()
        total = (await db.execute(count_stmt)).scalar() or 0
        
        return {
            "items": [r.to_dict() for r in rows],
            "total": int(total)
        }
    except Exception as e:
        print(f"Error listing sys exec logs: {e}")
        raise HTTPException(status_code=500, detail="server_error")

@router.post("/sys-exec-logs")
async def create_sys_exec_log(req: SysExecLogCreate, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        row = SysExecLog(
            user_id=req.user_id,
            description=req.description
        )
        db.add(row)
        await db.commit()
        return {"ok": True, "operation_id": str(row.operation_id)}
    except Exception as e:
        print(f"Error creating sys exec log: {e}")
        raise HTTPException(status_code=500, detail="server_error")

@router.delete("/sys-exec-logs/{operation_id}")
async def delete_sys_exec_log(operation_id: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        # Note: operation_id is UUID
        await db.execute(delete(SysExecLog).where(SysExecLog.operation_id == operation_id))
        await db.commit()
        return {"ok": True}
    except Exception as e:
        print(f"Error deleting sys exec log: {e}")
        raise HTTPException(status_code=500, detail="server_error")
