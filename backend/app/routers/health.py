from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """简单健康检查，用于开发阶段验证服务可用。"""
    return {"status": "ok"}
