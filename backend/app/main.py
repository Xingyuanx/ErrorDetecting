from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, health, secure, users, clusters, nodes, metrics, faults, ops, ai, hadoop_logs, sys_exec_logs, hadoop_exec_logs
import os

app = FastAPI(title="Hadoop Fault Detecting API", version="v1")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    将 Pydantic 校验错误转换为前端更易解析的格式
    """
    errors = []
    for error in exc.errors():
        field = error.get("loc")[-1] if error.get("loc") else "unknown"
        msg = error.get("msg")
        errors.append({
            "field": field,
            "message": f"{field}: {msg}",
            "code": error.get("type")
        })
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": {"errors": errors, "message": "请求参数校验失败"}}
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(secure.router, prefix="/api/v1")
app.include_router(clusters.router, prefix="/api/v1")
app.include_router(nodes.router, prefix="/api/v1")
app.include_router(metrics.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(hadoop_logs.router, prefix="/api/v1")
app.include_router(faults.router, prefix="/api/v1")
app.include_router(hadoop_exec_logs.router, prefix="/api/v1")
app.include_router(ops.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(sys_exec_logs.router, prefix="/api/v1")

