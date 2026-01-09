## 约束与目标
- 模型不本地部署，调用供应商 API（OpenAI/Azure/其他兼容）。
- 使用 Function Calling 技术，一个诊断智能体即可：可据集群日志判定故障并自动修复。
- 保障安全与可审计：角色校验、白名单工具、统一审计记录、流式输出。

## 架构简化
- 供应商客户端：`backend/app/services/llm.py`
  - `LLMClient(chat(messages, tools, stream))`，HTTPX 调用供应商 API，支持流式。
  - 读取 `.env`：`LLM_PROVIDER/LLM_ENDPOINT/LLM_MODEL/LLM_API_KEY`。
- 单智能体：`backend/app/agents/diagnosis_agent.py`
  - 输入：结构化日志查询结果 + 必要的原始日志截取。
  - 输出：根因 + 修复动作（通过 Function Calling 自动选择并执行工具）。
  - 循环：工具调用→结果回传模型→直至收敛或超时。
- 工具注册：`backend/app/services/ops_tools.py`
  - 已有能力复用：结构化日志（`backend/app/routers/logs.py:28`）、节点权限（`backend/app/routers/nodes.py:120`）、执行审计（`backend/app/routers/exec_logs.py`）。
  - 工具函数（提供 JSON Schema）：
    - `read_log(node, path, lines, pattern?)`
    - `kill_process(node, pid, signal)`
    - `reboot_node(node)`
    - `service_restart(node, service)`（可选：HDFS/YARN/NodeManager 等）
  - 入参校验 + `shlex.quote` + 白名单命令；统一落 `exec_logs`。
- API：`backend/app/routers/ai.py`
  - `POST /api/v1/ai/diagnose-repair`：触发单智能体诊断与自动修复（可选参数：集群/节点/时间窗/关键词/安全级别）。
  - `GET /api/v1/ai/stream/{taskId}`：SSE/WebSocket 流式返回模型推理与工具执行过程。

## 诊断与修复流程（单智能体）
1) 聚合上下文：
   - 查询结构化日志（数据库）`backend/app/routers/logs.py:28`（按 `level/op/node/cluster/time_from`）。
   - 若需要原始日志，调用工具 `read_log` 拉取尾部 N 行并可正则筛选。
   - 可选指标摘要：后续扩展 `metrics` 路由。
2) 发送到供应商 API（Function Calling）：
   - 系统提示：安全边界/只能调用注册工具/输出中文和结构化 JSON。
   - 提供工具签名（名称、说明、参数 schema）。
3) 模型选择工具并执行：
   - 后端按工具名调用实现（带节点权限校验与审计写入），将结果（stdout/stderr/exitCode）反馈给模型继续推理。
4) 收敛与输出：
   - 返回根因、执行的修复动作与结果、剩余风险与建议。
   - 写入 `exec_logs`（模型调用与工具执行）、必要时落 `faults`。

## 安全与审计
- 角色：默认要求 `ops` 或 `admin`；若设置 `auto=true` 且为 `admin` 可全自动。
- 命令白名单：工具层限定可执行命令（日志读取/kill/reboot/服务重启），禁止任意 shell。
- 审计：`exec_logs` 记录每次模型调用和工具执行（起止时间/退出码/操作者/影响节点）。
- 节点授权：沿用 `nodes` 访问校验（用户只能操作自己可访问集群）。

## 配置与依赖
- 仅供应商 API：新增 `httpx` 客户端与供应商 SDK（如 `openai`）。
- `.env` 注入密钥与模型信息；扩展 `backend/app/config.py` 读取，不写入日志。

## API 设计草案
- `POST /api/v1/ai/diagnose-repair`
  - 参数：`cluster?`、`node?`、`timeFrom?`、`keywords?`、`auto?`、`maxSteps?`。
  - 返回：`taskId`、`summary`、`actions`（工具名/参数/结果）、`rootCause`、`residualRisk`。
- `GET /api/v1/ai/stream/{taskId}`：流式 token + 工具结果。

## 代码落点与对接
- 复用：
  - 日志数据库查询：`backend/app/routers/logs.py:28`。
  - 审计：`backend/app/models/exec_logs.py:7`、`backend/app/routers/exec_logs.py:57`。
  - 节点授权：`backend/app/routers/nodes.py:120`。
- 新增：
  - `services/llm.py`（供应商 API 客户端 + Function Calling 包装）。
  - `services/ops_tools.py`（工具实现 + 审计写入 + 校验）。
  - `agents/diagnosis_agent.py`（单智能体循环与策略）。
  - `routers/ai.py`（统一入口 + 流式输出）。

## 迭代计划
- P0（2–3 天）：供应商客户端；`read_log/kill/reboot` 工具；单智能体基本循环；`/ai/diagnose-repair` 返回一次性结果（非流式）。
- P1（3–5 天）：SSE/WebSocket 流式输出；服务重启工具；风险分级参数（默认自动低风险）。
- P2（后续）：异常模式库与日志压缩；报表与可视化；缓存与限流。

## 验证
- 单元测试：工具参数校验、节点授权、审计写入；供应商 API 超时/重试。
- 集成测试：提供固定日志样本，验证模型能选择正确工具并完成修复；对高风险动作进行拒绝或需要 `admin`。