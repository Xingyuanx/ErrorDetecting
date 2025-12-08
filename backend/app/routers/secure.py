from fastapi import APIRouter, Depends
from ..deps.auth import get_current_user

router = APIRouter()

@router.get("/user/me")
async def me(user = Depends(get_current_user)):
    if isinstance(user, dict):
        return {"username": user.get("username"), "fullName": user.get("full_name"), "isActive": user.get("is_active")}
    return {"username": user.username, "fullName": user.full_name, "isActive": user.is_active}
