# 第十周周计划（沈永佳）

## 目标概述
- 完成数据库搭建与网络访问设置，确保局域网内后端可稳定连接数据库。
- 建好后台业务用户与权限，准备测试数据用于联调。
- 初始化后端框架，配置环境变量并跑通基础接口联调（登录/注册/健康检查）。

## 背景与依据
- 参考第九周周总结中提到的联调阻塞点（数据库准备与远程访问策略不足），本周以数据库与后端联通为核心推进。
  - 数据库访问策略：`pg_hba.conf`/`postgresql.conf`、账户权限与网络端口开放。
  - 后端连接配置：`backend/app/config.py:6-21` 读取 `.env` 的 `DATABASE_URL` 或分项变量。

## 任务清单
- 数据库搭建与网络设置
  - 安装并启动 PostgreSQL（或确认现有实例可用），创建业务数据库 `hadoop_fault_db`。
  - 配置 `postgresql.conf` 的 `listen_addresses` 为 `'*'` 或局域网地址。
  - 配置 `pg_hba.conf` 放行局域网网段，例如：`host    all    all    192.168.43.0/24    scram-sha-256`。
  - 开放 `5432` 端口并验证内网主机的连通性（telnet/nc/psql）。
- 后台用户与权限
  - 创建业务用户（如 `app_user`），授予目标库连接与基础读写权限。
  - 设置强口令与密码加密策略，记录账户与权限变更。
- 初始化与测试数据
  - 执行建表脚本：`doc/project/数据库建表脚本_postgres.sql`，创建核心表与初始数据（含 admin 显式映射）。
  - 插入测试用户与典型数据，用于登录/注册与状态查询联调。
- 初始化后端框架
  - 在 `backend/.env` 写入 `DATABASE_URL` 或 `DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD`，设置 `JWT_SECRET` 与 `JWT_EXPIRE_MINUTES`。
  - 安装依赖并启动后端：参考 `backend/README.md:73-92` 使用模块方式启动（`python -m uvicorn ...`）。
  - 基础接口验证：
    - 健康检查 `GET /api/v1/health`（`backend/app/routers/health.py`）。
    - 登录 `POST /api/v1/user/login`（`backend/app/routers/auth.py:25-50`）。
    - 注册 `POST /api/v1/user/register`（`backend/app/routers/auth.py:53-93`）。
    - 当前用户 `GET /api/v1/user/me`（`backend/app/routers/secure.py`）。
- 前端联调
  - 确认 `frontend-vue/vite.config.ts:6-18` 代理到后端地址或设置 `VITE_API_TARGET`。
  - 通过登录页面与 Store（`frontend-vue/src/app/stores/auth.ts:33-56, 58-75`）完成端到端登录/注册验证。
- 排障与文档
  - 记录失败场景（连接超时、认证失败、权限拒绝等），输出排障清单与解决步骤。
  - 更新 `backend/README.md` 如需补充环境与启动注意事项。

## 时间安排
- 周一：数据库安装与网络策略配置；开放端口与基础连通性验证。
- 周二：创建业务用户与权限；执行建表脚本与初始数据导入。
- 周三：配置后端环境变量与启动；联调健康检查与登录接口。
- 周四：联调注册与当前用户接口；完善错误提示与日志记录。
- 周五：前端代理与登录/注册端到端联调；整理排障清单与操作手册。

## 验收标准
- 局域网内后端可稳定连接数据库，基础 CRUD 与登录/注册流程通过。
- 前端能成功登录并获取 `Bearer` 令牌，携带访问受限接口返回正常。
- 排障文档覆盖常见失败场景，含操作步骤与验证方法。

## 产出物
- 数据库初始化与权限配置记录（含 `postgresql.conf`/`pg_hba.conf` 变更说明）。
- 测试数据与导入脚本或 SQL 清单。
- 后端环境与启动手册更新（如有变更）。
- 联调与排障清单（含 curl 示例与接口错误码对照）。
