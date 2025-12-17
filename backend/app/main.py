from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, health, secure, users, clusters, nodes, metrics, logs, faults, exec_logs, ops, ai, hadoop_logs

app = FastAPI(title="Hadoop Fault Detecting API", version="v1")

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
app.include_router(logs.router, prefix="/api/v1")
app.include_router(faults.router, prefix="/api/v1")
app.include_router(exec_logs.router, prefix="/api/v1")
app.include_router(ops.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(hadoop_logs.router, prefix="/api/v1")
