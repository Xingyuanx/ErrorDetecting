# Hadoop 故障诊断系统 - 后端服务 (FastAPI)

本项目是 Hadoop 故障诊断系统的后端核心，基于 FastAPI 构建，提供集群监控、日志采集、指标分析以及基于 AI 的智能故障诊断功能。

## 🚀 核心功能

- **用户与认证**: 基于 JWT 的无状态认证，支持用户注册、登录及权限管理。
- **集群与节点管理**: 支持 Hadoop 集群的注册、SSH 连通性校验、HDFS UUID 获取及节点状态管理。
- **指标采集与监控**: 
  - 自动采集集群及节点的 CPU、内存使用率。
  - 提供实时指标查询与趋势图数据支持。
- **Hadoop 日志管理**:
  - 远程日志读取：通过 SSH 实时读取各节点 Hadoop 日志。
  - 自动日志采集：增量 tail 模式采集日志并持久化至数据库。
  - 批量回填：支持对历史日志进行批量同步。
- **AI 智能诊断**:
  - 集成 LangChain 与 OpenAI，提供流式对话接口 (SSE)。
  - 智能智能体 (Agent) 可自动调用工具：查看日志、执行远程命令、分析集群状态。
- **系统执行日志**: 记录所有远程运维操作与系统任务的执行过程。

## 🛠 技术栈

- **框架**: [FastAPI](https://fastapi.tiangolo.com/) - 高性能异步 Web 框架。
- **数据库**: [PostgreSQL](https://www.postgresql.org/) + [SQLAlchemy (Async)](https://www.sqlalchemy.org/) - 异步 ORM 驱动。
- **SSH 通信**: [Paramiko](https://www.paramiko.org/) - 处理远程命令执行与日志读取。
- **AI/LLM**: [LangChain](https://www.langchain.com/) + OpenAI API - 实现故障诊断智能体。
- **任务调度**: 内置线程化采集器，支持异步指标与日志采集任务。
- **认证**: PyJWT + Passlib (BCrypt) - 安全的身份验证。

## 📂 项目结构

```text
backend/
├── app/
│   ├── agents/         # AI 智能体定义与工具编排
│   ├── deps/           # FastAPI 依赖注入（如认证、数据库）
│   ├── models/         # SQLAlchemy 异步模型
│   ├── routers/        # API 路由模块（集群、指标、日志、AI等）
│   ├── services/       # 业务逻辑服务（SSH管理、LLM调用等）
│   ├── workers/        # 异步任务处理逻辑
│   ├── config.py       # 环境变量与全局配置
│   ├── db.py           # 数据库引擎与会话管理
│   ├── main.py         # 应用入口与路由注册
│   └── log_collector.py # 日志采集器核心实现
├── scripts/            # 数据库初始化与验证脚本
├── tests/              # 单元测试与集成测试
├── requirements.txt    # 依赖清单
└── start_backend.sh    # 一键启动脚本
```

## ⚙️ 环境变量配置

在 `backend/` 目录下创建 `.env` 文件，配置如下关键参数：

| 参数 | 描述 | 默认值 |
| :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL 异步连接串 | `postgresql+asyncpg://postgres:password@localhost:5432/hadoop_fault_db` |
| `JWT_SECRET` | JWT 签名密钥 | `dev-secret` |
| `JWT_EXPIRE_MINUTES` | 令牌有效期（分钟） | `60` |
| `SSH_PORT` | 默认远程 SSH 端口 | `22` |
| `SSH_TIMEOUT` | SSH 连接超时时间 | `10` |
| `HADOOP_LOG_DIR` | Hadoop 远程日志默认路径 | `/usr/local/hadoop/logs` |
| `APP_TIMEZONE` | 系统时区 | `Asia/Shanghai` |
| `OPENAI_API_KEY` | OpenAI 密钥（用于 AI 诊断） | - |

## 🛠 安装与启动

### 1. 环境准备
- Python 3.10+
- PostgreSQL 14+

### 2. 安装依赖
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 初始化数据库
执行 `scripts/` 目录下的 SQL 脚本或通过内置脚本初始化：
```bash
# 导入 SQL 脚本
psql -h <host> -U <user> -d <db> -f ../doc/project/数据库建表脚本_postgres.sql
```

### 4. 启动服务
```bash
# 开发模式
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
或使用提供的启动脚本：
```bash
bash start_backend.sh
```

## 📖 API 接口预览

所有接口均带有 `/api/v1` 前缀。

- **Health**: `GET /health`
- **Auth**: `POST /auth/login`, `POST /auth/register`
- **Clusters**: `GET /clusters`, `POST /clusters/register`
- **Metrics**: `GET /metrics/trend`, `POST /metrics/collector/start`
- **Hadoop Logs**: `GET /hadoop/logs/all/{log_type}`, `GET /hadoop/collectors/status`
- **AI**: `POST /ai/chat` (支持 SSE 流式返回)

详细接口文档启动后访问：`http://localhost:8000/docs`

## 🧪 验证与测试
运行端到端验证脚本：
```bash
python scripts/verify_register.py
```
