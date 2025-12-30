from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from ..db import get_db
from ..models.users import User
from ..config import JWT_SECRET
import jwt

async def get_current_user(authorization: str | None = Header(None), db: AsyncSession = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="not_authenticated")
    token = authorization[7:]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="invalid_token")
        
        result = await db.execute(select(User).where(User.username == username).limit(1))
        user = result.scalars().first()
        
        if not user:
            # 如果是 demo 用户但不在 DB 中，创建一个临时的用户字典
            user_dict = {"username": username, "id": None, "is_active": True}
        else:
            if not user.is_active:
                raise HTTPException(status_code=403, detail="inactive_user")
            user_dict = {"username": user.username, "id": user.id, "is_active": user.is_active}

        # 获取权限列表
        perms_res = await db.execute(
            text("""
                SELECT DISTINCT p.permission_key 
                FROM permissions p
                JOIN role_permission_mapping rpm ON p.id = rpm.permission_id
                JOIN user_role_mapping urm ON rpm.role_id = urm.role_id
                JOIN users u ON urm.user_id = u.id
                WHERE u.username = :u
                UNION
                -- 兼容 demo 账号（如果不在 DB 中）
                SELECT DISTINCT p.permission_key
                FROM permissions p
                JOIN role_permission_mapping rpm ON p.id = rpm.permission_id
                JOIN roles r ON rpm.role_id = r.id
                WHERE (:u = 'admin' AND r.role_key = 'admin')
                   OR (:u = 'ops' AND r.role_key = 'operator')
                   OR (:u = 'obs' AND r.role_key = 'observer')
            """),
            {"u": username}
        )
        user_dict["permissions"] = [row[0] for row in perms_res.all()]
        return user_dict

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="token_expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="invalid_token")
    except Exception as e:
        print(f"Auth error: {e}")
        raise HTTPException(status_code=500, detail="auth_error")
