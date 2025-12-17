from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from ..db import get_db
from ..models.users import User
from passlib.hash import bcrypt
from ..config import JWT_SECRET, JWT_EXPIRE_MINUTES
import jwt
from datetime import datetime, timedelta, timezone
import re

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    fullName: str

@router.post("/user/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    demo = {"admin": "admin123", "ops": "ops123", "obs": "obs123"}
    if req.username in demo and req.password == demo[req.username]:
        exp = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
        token = jwt.encode({"sub": req.username, "exp": exp}, JWT_SECRET, algorithm="HS256")
        return {"ok": True, "username": req.username, "fullName": req.username, "token": token}
    try:
        result = await db.execute(select(User).where(User.username == req.username).limit(1))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=401, detail="invalid_credentials")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="inactive_user")
        if not bcrypt.verify(req.password, user.password_hash):
            raise HTTPException(status_code=401, detail="invalid_credentials")
        await db.execute(
            update(User).where(User.id == user.id).values(last_login=func.now(), updated_at=func.now())
        )
        await db.commit()
        exp = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
        token = jwt.encode({"sub": user.username, "exp": exp}, JWT_SECRET, algorithm="HS256")
        return {"ok": True, "username": user.username, "fullName": user.full_name, "token": token}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")

@router.post("/user/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        errors: list[dict] = []
        if not (3 <= len(req.username) <= 50) or not re.fullmatch(r"^[A-Za-z][A-Za-z0-9_]{2,49}$", req.username or ""):
            errors.append({"field": "username", "code": "invalid_username", "message": "用户名需以字母开头，支持字母/数字/下划线，长度3-50"})
        if not re.fullmatch(r"^[^@\s]+@[^@\s]+\.[^@\s]+", req.email or ""):
            errors.append({"field": "email", "code": "invalid_email", "message": "邮箱格式不正确"})
        if not (8 <= len(req.password) <= 128) or not re.search(r"[A-Z]", req.password) or not re.search(r"[a-z]", req.password) or not re.search(r"\d", req.password):
            errors.append({"field": "password", "code": "weak_password", "message": "密码至少8位，需包含大小写字母与数字"})
        if not (2 <= len(req.fullName) <= 100):
            errors.append({"field": "fullName", "code": "invalid_full_name", "message": "姓名长度需在2-100之间"})
        if errors:
            raise HTTPException(status_code=400, detail={"errors": errors})
        exists_username = await db.execute(select(User).where(User.username == req.username).limit(1))
        if exists_username.scalars().first():
            raise HTTPException(status_code=409, detail="user_exists")
        exists_email = await db.execute(select(User.id).where(User.email == req.email).limit(1))
        if exists_email.scalars().first():
            raise HTTPException(status_code=409, detail="email_exists")
        password_hash = bcrypt.hash(req.password)
        user = User(
            username=req.username,
            email=req.email,
            password_hash=password_hash,
            full_name=req.fullName,
            is_active=True,
            last_login=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(user)
        await db.flush()
        await db.commit()
        exp = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
        token = jwt.encode({"sub": user.username, "exp": exp}, JWT_SECRET, algorithm="HS256")
        return {"ok": True, "username": user.username, "fullName": user.full_name, "token": token}
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"server_error: {str(e)}")
