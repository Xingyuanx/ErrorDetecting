from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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
        try:
            result = await db.execute(select(User).where(User.username == username).limit(1))
            user = result.scalars().first()
            if user:
                if not user.is_active:
                    raise HTTPException(status_code=403, detail="inactive_user")
                return user
        except Exception:
            pass
        return {"username": username, "full_name": username, "is_active": True}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="token_expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="invalid_token")
