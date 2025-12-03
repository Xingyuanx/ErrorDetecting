from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import health, clusters, faults, logs

app = FastAPI(title="Hadoop Fault Detecting API", version="v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(clusters.router, prefix="/api/v1")
app.include_router(faults.router, prefix="/api/v1")
app.include_router(logs.router, prefix="/api/v1")