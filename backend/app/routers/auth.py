from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, text
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

async def _get_user_id(db: AsyncSession, username: str) -> int | None:
    res = await db.execute(text("SELECT id FROM users WHERE username=:u LIMIT 1"), {"u": username})
    row = res.first()
    return row[0] if row else None

async def _get_role_id(db: AsyncSession, role_key: str) -> int | None:
    res = await db.execute(text("SELECT id FROM roles WHERE role_key=:k LIMIT 1"), {"k": role_key})
    row = res.first()
    return row[0] if row else None

async def _ensure_observer_role(db: AsyncSession) -> int:
    rid = await _get_role_id(db, "observer")
    if rid is not None:
        return rid
    await db.execute(
        text(
            "INSERT INTO roles(role_name, role_key, description, is_system_role, created_at, updated_at) VALUES(:rn, :rk, :desc, TRUE, NOW(), NOW())"
        ),
        {"rn": "观察员", "rk": "observer", "desc": "系统默认观察员角色"},
    )
    await db.commit()
    rid2 = await _get_role_id(db, "observer")
    if rid2 is None:
        raise HTTPException(status_code=500, detail="role_init_failed")
    return rid2

async def _map_user_role(db: AsyncSession, username: str, role_key: str) -> None:
    uid = await _get_user_id(db, username)
    if uid is None:
        raise HTTPException(status_code=500, detail="user_not_found_after_register")
    rid = await _get_role_id(db, role_key)
    if rid is None:
        if role_key == "observer":
            rid = await _ensure_observer_role(db)
        else:
            raise HTTPException(status_code=400, detail="role_not_exist")
    await db.execute(text("DELETE FROM user_role_mapping WHERE user_id=:uid"), {"uid": uid})
    await db.execute(text("INSERT INTO user_role_mapping(user_id, role_id) VALUES(:uid, :rid)"), {"uid": uid, "rid": rid})
    await db.commit()

async def _get_user_roles(db: AsyncSession, user_id: int) -> list[str]:
    res = await db.execute(
        text("SELECT r.role_key FROM roles r JOIN user_role_mapping urm ON r.id = urm.role_id WHERE urm.user_id = :uid"),
        {"uid": user_id},
    )
    return [row[0] for row in res.all()]

async def _get_role_permissions(db: AsyncSession, role_keys: list[str]) -> list[str]:
    if not role_keys:
        return []
    res = await db.execute(
        text("""
            SELECT DISTINCT p.permission_key 
            FROM permissions p
            JOIN role_permission_mapping rpm ON p.id = rpm.permission_id
            JOIN roles r ON rpm.role_id = r.id
            WHERE r.role_key = ANY(:keys)
        """),
        {"keys": role_keys},
    )
    return [row[0] for row in res.all()]

@router.post("/user/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    demo = {"admin": "admin123", "ops": "ops123", "obs": "obs123"}
    if req.username in demo and req.password == demo[req.username]:
        exp = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
        token = jwt.encode({"sub": req.username, "exp": exp}, JWT_SECRET, algorithm="HS256")
        
        # 为 demo 账号获取角色和权限
        uid = await _get_user_id(db, req.username)
        roles = await _get_user_roles(db, uid) if uid else []
        if not roles:
            # 如果 DB 中没记录，给个默认
            role_map = {"admin": ["admin"], "ops": ["operator"], "obs": ["observer"]}
            roles = role_map.get(req.username, [])
        
        permissions = await _get_role_permissions(db, roles)
            
        return {
            "ok": True, 
            "username": req.username, 
            "fullName": req.username, 
            "token": token,
            "roles": roles,
            "permissions": permissions
        }
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
        
        # 获取用户角色和权限
        roles = await _get_user_roles(db, user.id)
        permissions = await _get_role_permissions(db, roles)
        
        exp = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
        token = jwt.encode({"sub": user.username, "exp": exp}, JWT_SECRET, algorithm="HS256")
        return {
            "ok": True, 
            "username": user.username, 
            "fullName": user.full_name, 
            "token": token,
            "roles": roles,
            "permissions": permissions
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="server_error")

@router.post("/user/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        errors: list[dict] = []
        # 用户名校验：3-50位，字母开头，支持字母/数字/下划线
        if not req.username or not (3 <= len(req.username) <= 50):
            errors.append({"field": "username", "code": "invalid_username", "message": "用户名长度需在3-50之间"})
        elif not re.fullmatch(r"^[A-Za-z][A-Za-z0-9_]*$", req.username):
            errors.append({"field": "username", "code": "invalid_username", "message": "用户名需以字母开头，仅支持字母、数字和下划线"})

        # 邮箱校验
        if not req.email or not re.fullmatch(r"^[^@\s]+@[^@\s]+\.[^@\s]+", req.email):
            errors.append({"field": "email", "code": "invalid_email", "message": "邮箱格式不正确"})

        # 密码校验：前端要求>=6位，后端要求>=8位并包含复杂性。为了兼容性调优提示。
        if not req.password or len(req.password) < 6:
            errors.append({"field": "password", "code": "weak_password", "message": "密码长度至少为6位"})
        elif len(req.password) < 8 or not re.search(r"[A-Z]", req.password) or not re.search(r"[a-z]", req.password) or not re.search(r"\d", req.password):
            errors.append({"field": "password", "code": "weak_password", "message": "密码建议至少8位，且包含大小写字母与数字"})

        # 姓名校验
        if not req.fullName or not (2 <= len(req.fullName) <= 100):
            errors.append({"field": "fullName", "code": "invalid_full_name", "message": "姓名长度需在2-100之间"})

        if errors:
            raise HTTPException(status_code=400, detail={"errors": errors, "message": errors[0]["message"]})

        # 检查唯一性
        exists_username = await db.execute(select(User).where(User.username == req.username).limit(1))
        if exists_username.scalars().first():
            raise HTTPException(status_code=400, detail={"message": "该用户名已被注册", "code": "user_exists"})

        exists_email = await db.execute(select(User.id).where(User.email == req.email).limit(1))
        if exists_email.scalars().first():
            raise HTTPException(status_code=400, detail={"message": "该邮箱已被绑定", "code": "email_exists"})
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
        await _map_user_role(db, req.username, "observer")
        permissions = await _get_role_permissions(db, ["observer"])
        
        exp = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
        token = jwt.encode({"sub": user.username, "exp": exp}, JWT_SECRET, algorithm="HS256")
        return {
            "ok": True, 
            "username": user.username, 
            "fullName": user.full_name, 
            "token": token,
            "roles": ["observer"],
            "permissions": permissions
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"server_error: {str(e)}")
