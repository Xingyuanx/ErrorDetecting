# 后端联调指南

## 环境与代理

- 前端目录：`frontend-vue`
- 开发代理：`frontend-vue/vite.config.ts:25-30` 将前端的 `/api` 代理到后端 `VITE_API_TARGET`
- 环境变量：
  - `frontend-vue/.env.development` 示例：`VITE_API_TARGET=https://your-backend.example.com`
  - 可选：`VITE_DEV_HOST`、`VITE_ALLOWED_HOSTS` 控制本地开发主机与允许的外网访问
- 启动与构建：
  - 开发：`cd frontend-vue && npm i && npm run dev`
  - 预览：`npm run preview`

## 鉴权与凭证

- 认证头：`Authorization: Bearer <token>`
- 前端存储：
  - `localStorage` 键名：`cm_user`、`cm_token`
  - 应用启动恢复：`frontend-vue/src/app/main.ts:10-12`
- 路由守卫：`frontend-vue/src/app/router/index.ts:23-30` 未登录重定向到登录页；基于 `meta.roles` 进行角色校验

## 关键接口规范

- 健康检查：`GET /v1/health`
- 登录：`POST /v1/user/login`
  - 请求体：`{ username, password }`
  - 响应体：`{ token, user: { username, role, email? } }`
- 注册：`POST /v1/user/register`
  - 请求体：`{ username, email, password, fullName }`
  - 响应体：`{ token?, user: { username, role, email? } }`
- 用户列表：`GET /api/v1/users`
  - 响应体：`{ users: Array<{ username, role, email }> }` 或 `Array<{ username, role, email }>`
  - 前端选择逻辑：仅匹配当前登录用户名；未匹配则显示错误提示
  - 权限不足（例如操作员 403）：页面显示权限提示
  - 角色值规范化：后端返回的 `role` 会统一转为小写并支持常见别名（如 `administrator`→`admin`、`ops`→`operator`）
- 集群与节点：
  - `GET /v1/clusters` → `[{ uuid, host, ip, count, health }]`
  - `POST /v1/clusters`、`DELETE /v1/clusters/:id`、`POST /v1/clusters/:id/start|stop`
  - `GET /v1/nodes?cluster=<uuid>` → `[{ name, ip, status, cpu, mem, updated }]`
  - `POST /v1/nodes/:name/start|stop`、`DELETE /v1/nodes/:name`
- 指标：
  - CPU 趋势：`GET /v1/metrics/cpu_trend?cluster=<uuid>` → `{ times: string[], values: number[] }`
  - 内存使用：`GET /v1/metrics/memory_usage?cluster=<uuid>` → `{ used: number, free: number }`
- 诊断：
  - 故障摘要：`GET /v1/faults/summary?node=<name>|cluster=<host>` → `{ code, time, scope }`
  - AI 对话历史：`GET /v1/ai/history?sessionId=<id>` → `{ messages: Array<{ role, content, reasoning? }> }`
  - AI 对话：`POST /v1/ai/chat` → `{ reply, reasoning? }`

## 前端数据绑定要点

- 个人主页：`frontend-vue/src/app/views/Profile.vue`
  - 仅使用后端数据；加载中与错误态可视化
  - 角色标签映射：`frontend-vue/src/app/constants/roles.ts`
- 角色来源：
  - 登录/注册优先采用后端返回的 `user.role` 或 `role`（`frontend-vue/src/app/stores/auth.ts:55-72,74-91`）
- 诊断页与导航：
  - 路由授权：`diagnosis` 允许 `admin/operator`（`frontend-vue/src/app/router/index.ts:12`）
  - 侧边栏入口基于角色显示（`frontend-vue/src/app/components/Sidebar.vue:7`）

## 联调步骤

- 设置 `VITE_API_TARGET` 指向后端地址，确保后端允许来自前端的 CORS 与 Host
- 启动前端后检查 `GET /v1/health` 返回正常
- 使用真实账号登录，确认：
  - `GET /v1/user/me` 返回用户信息，个人主页字段显示为后端数据
  - 侧边栏与页面访问受角色控制
  - 仪表板与诊断页数据来自后端接口
- 常见问题：
  - Token 无效或过期 → 返回 `401`，需要重新登录
  - 代理失败 → 检查 `VITE_API_TARGET` 与后端协议/端口
  - 外网访问本地开发 → 配置 `VITE_ALLOWED_HOSTS`，参考 `Cloudflare-Tunnel-Guide.md`

## 参考文件

- `frontend-vue/vite.config.ts`
- `frontend-vue/src/app/main.ts`
- `frontend-vue/src/app/router/index.ts`
- `frontend-vue/src/app/stores/auth.ts`
- `frontend-vue/src/app/views/Profile.vue`
- `frontend-vue/src/app/components/Sidebar.vue`
- `frontend-vue/src/app/constants/roles.ts`
