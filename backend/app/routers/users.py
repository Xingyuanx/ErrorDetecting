from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from ..db import get_db
from ..models.users import User
from ..deps.auth import get_current_user
from passlib.hash import bcrypt
from datetime import datetime, timezone
import re

router = APIRouter()

ROLE_OVERRIDES: dict[str, str] = {}


class CreateUserRequest(BaseModel):
    username: str
    email: str
    role: str
    status: str


class UpdateUserRequest(BaseModel):
    role: str | None = None
    status: str | None = None


def _status_to_active(status: str) -> bool:
    return status == "enabled"


def _active_to_status(active: bool) -> str:
    return "enabled" if active else "disabled"


def _role_or_default(username: str) -> str:
    if username in ROLE_OVERRIDES:
        return ROLE_OVERRIDES[username]
    if username == "admin":
        return "admin"
    if username == "ops":
        return "operator"
    if username == "obs":
        return "observer"
    return "observer"


def _get_username(u) -> str:
    return getattr(u, "username", None) or (u.get("username") if isinstance(u, dict) else None)


def _require_admin(u):
    name = _get_username(u)
    if name != "admin":
        raise HTTPException(status_code=403, detail="not_admin")


@router.get("/users")
async def list_users(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        _require_admin(user)
        result = await db.execute(select(User).limit(500))
        rows = result.scalars().all()
        users = [
            {
                "username": u.username,
                "email": u.email,
                "role": _role_or_default(u.username),
                "status": _active_to_status(u.is_active),
            }
            for u in rows
        ]
        return {"users": users}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


@router.post("/users")
async def create_user(req: CreateUserRequest, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        _require_admin(user)
        errors: list[dict] = []
        if not (3 <= len(req.username) <= 50) or not re.fullmatch(r"^[A-Za-z][A-Za-z0-9_]{2,49}$", req.username or ""):
            errors.append({"field": "username", "message": "用户名需以字母开头，支持字母/数字/下划线，长度3-50"})
        if not re.fullmatch(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", req.email or ""):
            errors.append({"field": "email", "message": "邮箱格式不正确"})
        if req.role not in {"admin", "operator", "observer"}:
            errors.append({"field": "role", "message": "角色必须为 admin/operator/observer"})
        if req.status not in {"enabled", "pending", "disabled"}:
            errors.append({"field": "status", "message": "状态必须为 enabled/pending/disabled"})
        if errors:
            raise HTTPException(status_code=400, detail={"errors": errors})

        exists_username = await db.execute(select(User.id).where(User.username == req.username).limit(1))
        if exists_username.scalars().first():
            raise HTTPException(status_code=409, detail={"errors": [{"field": "username", "message": "用户名已存在"}]})
        exists_email = await db.execute(select(User.id).where(User.email == req.email).limit(1))
        if exists_email.scalars().first():
            raise HTTPException(status_code=409, detail={"errors": [{"field": "email", "message": "邮箱已存在"}]})

        temp_password = "TempPass#123"
        password_hash = bcrypt.hash(temp_password)
        now = datetime.now(timezone.utc)
        user_obj = User(
            username=req.username,
            email=req.email,
            password_hash=password_hash,
            full_name=req.username,
            is_active=_status_to_active(req.status),
            last_login=None,
            created_at=now,
            updated_at=now,
        )
        db.add(user_obj)
        await db.flush()
        await db.commit()
        ROLE_OVERRIDES[req.username] = req.role
        return {"ok": True}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


@router.patch("/users/{username}")
async def update_user(username: str, req: UpdateUserRequest, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        _require_admin(user)
        result = await db.execute(select(User).where(User.username == username).limit(1))
        u = result.scalars().first()
        if not u:
            raise HTTPException(status_code=404, detail="not_found")
        updates = {}
        if req.status is not None:
            if req.status not in {"enabled", "disabled"}:
                raise HTTPException(status_code=400, detail="invalid_status")
            updates["is_active"] = _status_to_active(req.status)
        if req.role is not None:
            if req.role not in {"admin", "operator", "observer"}:
                raise HTTPException(status_code=400, detail={"errors": [{"field": "role", "message": "不允许的角色"}]})
            ROLE_OVERRIDES[username] = req.role
        if updates:
            updates["updated_at"] = func.now()
            await db.execute(update(User).where(User.id == u.id).values(**updates))
            await db.commit()
        return {"ok": True}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")


@router.delete("/users/{username}")
async def delete_user(username: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        _require_admin(user)
        result = await db.execute(select(User).where(User.username == username).limit(1))
        u = result.scalars().first()
        if not u:
            ROLE_OVERRIDES.pop(username, None)
            return {"ok": True}
        await db.execute(delete(User).where(User.id == u.id))
        await db.commit()
        ROLE_OVERRIDES.pop(username, None)
        return {"ok": True}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")
