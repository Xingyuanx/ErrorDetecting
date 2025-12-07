from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from ..db import get_db
from ..models.users import User
from passlib.hash import bcrypt

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/user/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """处理登录请求，验证用户名与密码。"""
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
    return {"ok": True, "username": user.username, "fullName": user.full_name}
