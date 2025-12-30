# 邢远鑫第 14 周个人周计划

第 14 周（2025-12-22 至 2025-12-28）

**核心目标**：完成下列模块的前后端联调与体验完善，形成可回归、可验收的功能闭环

1. 完善“注册新集群”功能的前后端联调（第 13 周为半成品）
2. 完成“执行日志”模块的前后端联调
3. 完善“故障诊断”模块的前后端联调
4. 完成“告警配置”的前后端联调
5. 完成“操作日志”的前后端联调
6. 完成“账号管理”的前后端联调
7. 完成“搜索”功能

**前置准备**：

- 前端结构与路径：`frontend-vue/src/app/views/*.vue`、`components/*.vue`、`router/index.ts`、`stores/auth.ts`、`constants/roles.ts`、`lib/api.ts`
- 后端接口契约：集群（`/api/v1/clusters`、`/start|/stop|/unregister`）、节点（`/api/v1/nodes`）、执行日志（`/api/v1/exec-logs`）、诊断 AI（`/api/v1/ai/history`、`/api/v1/ai/chat`）、日志检索（`/api/v1/logs`）、用户与角色（`/api/v1/users`）
- 联调文档与配置：`backend_register_cluster_guide.md`、`vite.config.ts` 代理 `/api`、演示登录兜底（`auth.ts`）

## 周一：注册新集群联调完善（ClusterList）

- 完善表单与参数校验（SSH、主机、端口、凭证），统一错误提示与禁用态
- 对接 `POST /api/v1/clusters`（或 Hadoop 扩展接口），保存后刷新列表与路由跳转
- 启停与注销操作对接：`POST /api/v1/clusters/{id}/start|stop`、`DELETE /api/v1/clusters/{id}`
- 联动仪表与节点：设置 `current_cluster` 后，`Dashboard.vue` 与节点列表拉取 `GET /api/v1/nodes?cluster=...`
- 验收：能新增/启停/注销集群；状态与错误反馈清晰；仪表与节点联动正常

## 周二：执行日志模块联调（ExecLogs）

- 列表分页/筛选对接 `GET /api/v1/exec-logs`，统一加载与错误提示
- 录入与编辑对接 `POST /api/v1/exec-logs`、`PUT /api/v1/exec-logs/{id}`，删除对接 `DELETE /api/v1/exec-logs/{id}`
- 组件抽象与交互优化：`ExecLogsTable.vue` 支持列配置与服务端分页
- 验收：增删改查完整闭环；分页与筛选生效；错误与成功提示一致

## 周三：故障诊断联调完善（Diagnosis）

- 左侧集群/节点联动：`GET /api/v1/clusters`、`GET /api/v1/nodes?cluster=...`
- 故障摘要与日志预览：`GET /api/v1/faults/summary`、`GET /api/v1/logs?...`
- AI 历史与会话：`GET /api/v1/ai/history?sessionId=...`、`POST /api/v1/ai/chat`（携带上下文与选中节点/模型）
- 统一错误展示（红色高亮、多行详情）与消息中心策略（网络失败与重试）
- 验收：故障信息与日志预览可用；AI 对话历史与发送正常；异常反馈统一

## 周四：告警配置联调（AlertConfig）

- 将页面原型接入后端告警配置接口（按后端契约：规则查询/新增/更新/删除）
- 表单校验与规则启停、阈值/级别设置；支持批量启停与删除
- 验收：规则列表增删改查闭环；启停/阈值更新即时生效；统一错误提示

## 周五：操作日志联调（AuditLogs）

- 对接审计日志接口（操作人、节点/集群、指令、时间、结果），支持分页与筛选
- 与集群/节点操作打通（注册/启停/注销等动作产生审计记录）
- 验收：可查询与过滤审计日志；操作后能看到对应记录；导出基础能力

## 周六：账号管理联调（UserManagement/Profile）

- 用户列表/创建/更新/删除对接：`GET /api/v1/users`、`POST /api/v1/users`、`PATCH /api/v1/users/{id}`、`DELETE /api/v1/users/{id}`
- 内联角色选择与密码/确认字段校验；`Profile.vue` 用户信息读取规范化
- 验收：用户 CRUD 完整；角色切换与登录态一致；表单校验与提示规范

## 周日：搜索功能完善（HeaderNav/Logs）

- 全局搜索输入对接路由与查询参数；支持在各视图中高亮命中项
- 日志搜索页对接 `GET /api/v1/logs` 多维过滤（来源/级别/集群/节点/服务/时间）；结果列表高亮显示
- 验收：全局跳转与命中高亮有效；日志搜索多条件过滤稳定；性能与体验可接受

## 交付物

- 集群注册/管理闭环、执行日志 CRUD、诊断与 AI 联动、告警与审计日志、账号管理、搜索功能
- 统一的错误提示与消息策略、禁用态与加载态规范
- 联调文档更新与接口契约对齐（含变更清单）

## 验收标准

- 每个模块完成接口对接与页面可用性；失败与成功反馈一致可感知
- 集群 → 仪表/节点联动正确；操作后审计记录可查询
- 执行日志与告警配置具备增删改查闭环；诊断具备日志预览与 AI 对话闭环
- 账号管理 CRUD 可用；全局搜索与日志搜索体验一致
- 联调文档可复用且与实现一致

---

**计划人**：邢远鑫  
**计划周期**：第 14 周
