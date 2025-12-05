from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class LoginPayload(BaseModel):
    username: str
    password: str

class RegisterPayload(BaseModel):
    username: str
    password: str
    contact: str
    role: str

class Cluster(BaseModel):
    uuid: str
    master_host: str
    master_ip: str
    node_count: int
    health: str

class LogItem(BaseModel):
    time: str
    level: str
    cluster: str
    node: str
    op: str
    user: str
    message: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/auth/login")
def login(payload: LoginPayload):
    demo = {
        "admin": {"p": "admin123", "role": "admin"},
        "ops": {"p": "ops123", "role": "operator"},
        "obs": {"p": "obs123", "role": "observer"},
    }
    info = demo.get(payload.username)
    if info and info["p"] == payload.password:
        token = f"demo-token-{payload.username}-{int(time.time())}"
        return {"ok": True, "token": token, "role": info["role"], "username": payload.username}
    return {"ok": False, "message": "invalid credentials"}

@app.post("/auth/register")
def register(payload: RegisterPayload):
    return {"ok": True, "status": "pending"}

@app.get("/clusters", response_model=List[Cluster])
def list_clusters():
    return [
        {"uuid": "CL-1111-AAAA", "master_host": "namenode-a", "master_ip": "192.168.10.10", "node_count": 12, "health": "running"},
        {"uuid": "CL-2222-BBBB", "master_host": "namenode-b", "master_ip": "192.168.10.20", "node_count": 8, "health": "warning"},
        {"uuid": "CL-3333-CCCC", "master_host": "namenode-c", "master_ip": "192.168.10.30", "node_count": 4, "health": "error"},
    ]

@app.get("/logs", response_model=List[LogItem])
def list_logs():
    return [
        {
            "time": "2025-11-07T10:30:15Z",
            "level": "error",
            "cluster": "CL-3333-CCCC",
            "node": "CL-3333-CCCC-003",
            "op": "security",
            "user": "alice",
            "message": "连接超时：无法连接到 DataNode，尝试次数=3，超时=5s"
        },
        {
            "time": "2025-11-07T10:29:42Z",
            "level": "warn",
            "cluster": "CL-2222-BBBB",
            "node": "CL-2222-BBBB-002",
            "op": "system",
            "user": "ops",
            "message": "CPU 使用率连续5分钟超过80%，任务队列长度=27"
        },
        {
            "time": "2025-11-07T10:28:33Z",
            "level": "info",
            "cluster": "CL-1111-AAAA",
            "node": "CL-1111-AAAA-001",
            "op": "maintenance",
            "user": "obs",
            "message": "心跳: OK"
        }
    ]
