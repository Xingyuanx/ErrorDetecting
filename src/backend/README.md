# 后端代码结构说明（FastAPI + SQLAlchemy + asyncpg）

## 目录结构
- `src/backend/requirements.txt`：Python 依赖列表
- `src/backend/app/main.py`：应用入口与路由注册
- `src/backend/app/config.py`：配置加载（环境变量、数据库连接串）
- `src/backend/app/db.py`：数据库引擎与会话管理（异步）
- `src/backend/app/models/`：SQLAlchemy 模型（PostgreSQL 原生类型对齐）
- `src/backend/app/routers/`：API 路由（按模块划分）

## 关键模块
- 应用入口：`src/backend/app/main.py`
  - 注册中间件（CORS）与路由前缀 `/api/v1`
  - 挂载模块：`health`、`clusters`、`faults`、`logs`
- 配置加载：`src/backend/app/config.py`
  - 环境变量 `DATABASE_URL`（默认：`postgresql+asyncpg://postgres:password@localhost:5432/hadoop_fault_db`）
- 数据库会话：`src/backend/app/db.py`
  - 创建 `AsyncEngine` 与 `async_sessionmaker`
  - 依赖注入函数 `get_db()` 提供异步会话
- 模型层：`src/backend/app/models/`
  - `clusters.py`：`JSONB`、`UUID`、`TIMESTAMPTZ` 字段对齐
  - `fault_records.py`：支持 `affected_nodes`/`affected_clusters`（JSONB）
  - `exec_logs.py`：执行日志（文本/JSONB/时间/状态）
  - `system_logs.py`：系统日志（文本/时间/级别/处理标记）
- 路由层：`src/backend/app/routers/`
  - `health.py`：`GET /api/v1/health`（连通性检查）
  - `clusters.py`：`GET /api/v1/clusters`（列表）
  - `faults.py`：`GET /api/v1/faults`（列表）
  - `logs.py`：`GET /api/v1/logs`（按级别筛选与分页）

## 运行方式
- 创建并激活虚拟环境、安装依赖：
```
python -m venv venv
venv\Scripts\activate
pip install -r src/backend/requirements.txt
```
- 配置环境变量（或 `.env`）：
```
DATABASE_URL=postgresql+asyncpg://postgres:<安全口令>@localhost:5432/hadoop_fault_db
```
- 启动服务（Windows PowerShell）：
```
uvicorn src.backend.app.main:app --reload
```

## API 约定
- 前缀：`/api/v1`
- 返回结构：
  - 列表：`{ "total": <int>, "list": [...] }`
  - 错误包络（建议）：`{ "code": <int>, "message": "<string>", "detail": { ... }, "traceId": "<uuid>" }`
- 常用查询：
  - 日志：`GET /api/v1/logs?level=&page=&pageSize=`

## 数据库类型对齐
- JSON：`JSONB`
- IP：`INET`
- 时间：`TIMESTAMPTZ`（后端使用 `TIMESTAMP(timezone=True)` 映射）
- 主键：`GENERATED ALWAYS AS IDENTITY`

## 后续扩展建议
- 增加 Pydantic `schemas`（输入/输出）与 `POST` 接口（例如新增集群、新增故障）
- 引入 WebSocket `/ws/status` 与 `/ws/diagnose` 支持实时推送
- 加入审计与权限模块（`roles`/`permissions`/`user_role_mapping` 等）
- 接入 Prometheus 指标与 Grafana 看板（接口耗时、错误率、WS 在线率）

## 登录与认证（实现规划）
- 依赖：`passlib[bcrypt]` 或 `bcrypt`、`python-jose[cryptography]`
- 路由：`POST /api/v1/user/login`（用户名/密码）返回 `access_token`；`GET /api/v1/user/me` 返回当前用户信息
- 认证：JWT Bearer；环境变量 `JWT_SECRET` 与 `JWT_EXPIRE_MINUTES`
- 审计：登录成功/失败在 `audit_logs` 记录 `action=login/login_failed`
- 前端：登录页调用登录接口，保存 `access_token` 到 `localStorage`，Axios 拦截器注入 `Authorization: Bearer <token>`
