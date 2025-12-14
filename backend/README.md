# 后端部署与启动指南

本指南介绍如何在本地或服务器环境部署并启动后端服务（FastAPI）。后端默认提供 `/api/v1` 前缀的接口，前端通过 Vite 代理到该服务。

## 环境准备
- 操作系统：Windows/Linux/Mac 均可
- 必备软件：
  - Python 3.10+（建议 3.10 或以上）
  - PostgreSQL 14+（或兼容版本）
- 代码位置：`backend/` 为后端根目录

## 安装依赖
1) 创建并激活虚拟环境（Windows 示例）：
```
cd backend
python -m venv .venv
.\.venv\Scripts\activate
```
Linux/Mac 示例：
```
cd backend
python3 -m venv .venv
source .venv/bin/activate
```
2) 安装依赖：
```
pip install -r requirements.txt
```

## 数据库配置
后端通过环境变量读取数据库连接，优先使用 `DATABASE_URL`；若未设置，则使用 `DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD` 组合。

- 方式一：设置组合连接串 `DATABASE_URL`
```
# .env
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:<port>/<db>
JWT_SECRET=please-change-it
JWT_EXPIRE_MINUTES=60
```
- 方式二：分别设置参数
```
# .env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hadoop_fault_db
DB_USER=postgres
DB_PASSWORD=your_password
JWT_SECRET=please-change-it
JWT_EXPIRE_MINUTES=60
```
配置文件读取逻辑见 `backend/app/config.py`，默认值为：
- `DATABASE_URL` 默认 `postgresql+asyncpg://postgres:password@localhost:5432/hadoop_fault_db`
- `JWT_SECRET` 默认 `dev-secret`
- `JWT_EXPIRE_MINUTES` 默认 `60`

## 初始化数据库
项目提供 PostgreSQL 建表脚本，含核心业务表与初始数据：
- 脚本路径：`doc/project/数据库建表脚本_postgres.sql`

使用 `psql` 导入（Windows 示例）：
```
psql -h <host> -U <user> -d <db> -f "doc/project/数据库建表脚本_postgres.sql"
```
Linux/Mac 示例：
```
psql -h <host> -U <user> -d <db> -f ./doc/project/数据库建表脚本_postgres.sql
```

> 提示：若需远程访问 PostgreSQL，请确认：
> - `postgresql.conf` 中 `listen_addresses='*'`（或包含服务器地址）
> - `pg_hba.conf` 中允许来源网段，例如：`host    all    all    192.168.43.0/24    scram-sha-256`

## 启动数据库
PostgreSQL 15 启动与管理：

pg_ctl 方式（受限环境推荐）：
```
# 启动
sudo -u postgres /usr/lib/postgresql/15/bin/pg_ctl -D /var/lib/postgresql/15/main -o "-c config_file=/etc/postgresql/15/main/postgresql.conf" -l /var/log/postgresql/postgresql-15-main.log start
# 状态
sudo -u postgres /usr/lib/postgresql/15/bin/pg_ctl -D /var/lib/postgresql/15/main status
# 停止
sudo -u postgres /usr/lib/postgresql/15/bin/pg_ctl -D /var/lib/postgresql/15/main stop
# 重启
sudo -u postgres /usr/lib/postgresql/15/bin/pg_ctl -D /var/lib/postgresql/15/main restart
```

systemd 方式（标准环境）：
```
# 启动所有集群
sudo systemctl start postgresql
# 启动指定实例（根据系统实际单元名可能为 postgresql@15-main）
sudo systemctl start postgresql@15-main
# 查看状态
sudo systemctl status postgresql
sudo systemctl status postgresql@15-main
```
进入psql命令行：
PGPASSWORD='shenyongye123da*' psql -h 127.0.0.1 -U echo -d hadoop_fault_db
开机自启动：
```
# 所有集群自启
sudo systemctl enable postgresql
# 指定实例自启
sudo systemctl enable postgresql@15-main
```

取消自启动与验证：
```
# 取消自启（指定实例）
sudo systemctl disable postgresql@15-main
# 查看是否启用（enabled/disabled）
systemctl is-enabled postgresql@15-main
# 重启后验证监听状态
sudo -u postgres /usr/lib/postgresql/15/bin/pg_isready
```

连接验证：
```
# 管理员
export PGPASSWORD='password'
psql -h 127.0.0.1 -U postgres -d hadoop_fault_db -c "SELECT 1;"
# 应用账户 echo
export PGPASSWORD='shenyongye123da*'
psql -h 127.0.0.1 -U echo -d hadoop_fault_db -c "SELECT current_user;"
```

日志查看：
```
sudo tail -n 100 /var/log/postgresql/postgresql-15-main.log
```

## 启动服务
开发模式（自动重载）：
```
# 通用方式（推荐）
进入backend目录:
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Windows 若未配置 python 到 PATH，可使用 Python Launcher：
在backend目录中:
py -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 使用虚拟环境中的解释器（绝对可靠）：
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
生产模式（示例，仅供参考）：
```
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
# 或 Windows：
py -m uvicorn app.main:app --host 0.0.0.0 --port 8000
# 或使用虚拟环境解释器：
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

前端代理默认将 `/api` 代理到 `http://localhost:8000`。如需修改，在 `frontend-vue/vite.config.ts` 中设置 `VITE_API_TARGET`。

## 快速联调
健康检查：
```
curl http://localhost:8000/api/v1/health
```
注册用户：
```
curl -X POST http://localhost:8000/api/v1/user/register \
  -H "Content-Type: application/json" \
  -d '{
    "username":"user001",
    "email":"user001@example.com",
    "password":"StrongPass1",
    "fullName":"测试用户"
  }'
```
登录获取令牌：
```
curl -X POST http://localhost:8000/api/v1/user/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user001","password":"StrongPass1"}'
```
携带令牌访问当前用户：
```
curl http://localhost:8000/api/v1/user/me -H "Authorization: Bearer <token>"
```

## 可选：本地验证脚本
项目已提供端到端验证脚本：`backend/scripts/verify_register.py`

在已激活的虚拟环境中运行（Windows 示例）：
```
.\.venv\Scripts\python.exe .\scripts\verify_register.py
```
Linux/Mac 示例：
```
python ./scripts/verify_register.py
```

## 接口清单（节选）
- `GET /api/v1/health` 健康检查
- `POST /api/v1/user/register` 注册新用户，返回 `token`
- `POST /api/v1/user/login` 登录并返回 `token`
- `GET /api/v1/user/me` 获取当前用户信息（需 `Authorization: Bearer <token>`）

## 其他说明
- 演示账户（仅用于快速体验）：`admin/admin123`、`ops/ops123`、`obs/obs123`
- 安全建议：生产环境务必设置强随机的 `JWT_SECRET`，并限制数据库访问来源
- 若依赖安装失败或 `python` 命令不可用，请确认已安装 Python 并将其加入系统 PATH，或使用虚拟环境中的解释器路径运行命令
