# AI 工具调用测试提示词（/api/v1/ai/chat）

本页用于前端/测试同学对接与验证 AI 工具调用能力。所有提示词都建议通过 `/api/v1/ai/chat` 发送，并在消息里带上必要的 `cluster_uuid / node / log_type / path` 等信息，确保模型能直接触发工具调用。

## 通用前置条件

- 已能正常登录并拿到 token
- 已有至少 1 个可用集群 UUID（记为 `<CLUSTER_UUID>`）
- 集群已录入 NameNode/RM 的 IP 与密码（否则涉及 Namenode/RM 的命令会返回未配置）
- 当前登录用户已被映射到该集群（否则会返回 forbidden）
- 如需指定节点：准备 1 个节点 hostname（记为 `<NODE_HOSTNAME>`）
- 如需读取具体文件：准备 1 个路径（记为 `<LOG_PATH>`）

## 使用方式（推荐）

- 接口：`POST /api/v1/ai/chat`
- Body 示例（非流式）：

```json
{
  "sessionId": "test-ai-tools",
  "message": "这里放测试提示词",
  "stream": false,
  "context": { "model": "可选:你的模型名" }
}
```

## 1. 故障识别：detect_cluster_faults

### 1.1 默认组件（namenode + resourcemanager）

提示词：

> 我在集群 `<CLUSTER_UUID>` 上怀疑出现故障。请先调用 detect_cluster_faults 分析 namenode 和 resourcemanager 的最近 200 行日志，给出根因、证据行与建议。

期望：

- 模型触发 `detect_cluster_faults`，并返回 `faults` 列表（可能为空）
- 回答中包含：根因推断、影响范围、证据（examples）与建议（advice）

### 1.2 指定组件列表

提示词：

> 集群 `<CLUSTER_UUID>` 的 YARN 任务提交失败。请调用 detect_cluster_faults，components 传入 ["resourcemanager"]，lines=200，输出结构化故障结论。

期望：

- tools: `detect_cluster_faults(components=["resourcemanager"])`

### 1.3 负向：UUID 格式错误

提示词：

> 请对集群 `not-a-uuid` 调用 detect_cluster_faults 分析故障。

期望：

- 工具返回 `invalid_uuid_format`，模型应解释 UUID 不合法并提示正确格式

## 2. 组件日志读取：read_cluster_log

### 2.1 读取 NameNode 日志

提示词：

> 读取集群 `<CLUSTER_UUID>` 的 namenode 日志最近 100 行。请调用 read_cluster_log。

期望：

- 工具返回 `status=success` 且包含 `content`（若找不到日志应给出原因 message）

### 2.2 读取 ResourceManager 日志

提示词：

> 读取集群 `<CLUSTER_UUID>` 的 resourcemanager 日志最近 200 行（lines=200）。请调用 read_cluster_log 并把关键错误行摘出来。

期望：

- `read_cluster_log(log_type="resourcemanager", lines=200)`

### 2.3 指定节点主机名（多实例组件建议）

提示词：

> 集群 `<CLUSTER_UUID>` 的 datanode 日志我只想看 `<NODE_HOSTNAME>` 这台。请调用 read_cluster_log，log_type=datanode，node_hostname=`<NODE_HOSTNAME>`，lines=120。

期望：

- `read_cluster_log` 能根据 node_hostname 定位到节点并读取匹配日志文件（可能返回 log_file_not_found，但应给出解释）

## 3. 单节点任意文件读取：read_log

### 3.1 读取指定路径尾部

提示词：

> 在节点 `<NODE_HOSTNAME>` 上读取文件 `<LOG_PATH>` 的最后 200 行。请调用 read_log。

期望：

- 工具返回 `exitCode=0` 且 stdout 含日志内容

### 3.2 带正则筛选（grep -E）

提示词：

> 在节点 `<NODE_HOSTNAME>` 上读取 `<LOG_PATH>` 最后 500 行，并筛选包含 "ERROR|Exception" 的行。请调用 read_log，lines=500，pattern="ERROR|Exception"。

期望：

- stdout 更聚焦于错误行

### 3.3 负向：无权限节点

提示词：

> 在节点 `some_other_node` 上读取 `/var/log/messages` 最后 50 行。请调用 read_log。

期望：

- 工具返回 `node_not_found`（代表当前用户不可访问或节点不存在），模型应解释权限限制

## 4. 集群运维命令：run_cluster_command（白名单）

说明：此工具只能执行白名单 `command_key`，无法执行任意命令字符串。

### 4.1 进程检查：jps（默认 all_nodes）

提示词：

> 请对集群 `<CLUSTER_UUID>` 执行 jps 检查所有节点的 Java 进程（run_cluster_command，command_key=jps）。输出每个节点的关键进程。

期望：

- 返回 `results` 数组，每个元素包含 node/ip/exitCode/stdout/stderr

### 4.2 版本信息：hadoop_version（namenode）

提示词：

> 我想确认集群 `<CLUSTER_UUID>` 的 Hadoop 版本。请调用 run_cluster_command，command_key=hadoop_version，并总结版本号。

### 4.3 HDFS 总览：hdfs_report（namenode）

提示词：

> 对集群 `<CLUSTER_UUID>` 执行 hdfs_report，给出 DataNode 数量、总容量、已用容量的摘要。

### 4.4 SafeMode 状态：hdfs_safemode_get（namenode）

提示词：

> 对集群 `<CLUSTER_UUID>` 执行 hdfs_safemode_get，告诉我当前是否处于 SafeMode，并给出下一步建议。

### 4.5 YARN 节点：yarn_node_list（resourcemanager）

提示词：

> 对集群 `<CLUSTER_UUID>` 执行 yarn_node_list，输出节点数量，并列出前 5 个节点信息。

### 4.6 YARN 应用：yarn_application_list（resourcemanager）

提示词：

> 对集群 `<CLUSTER_UUID>` 执行 yarn_application_list，给出当前 RUNNING 的应用数量和应用 ID 列表（最多 20 个）。

### 4.7 系统资源：df_h / free_h / uptime（all_nodes）

提示词（任选其一）：

> 对集群 `<CLUSTER_UUID>` 执行 df_h，汇总磁盘使用率最高的 3 台节点。

> 对集群 `<CLUSTER_UUID>` 执行 free_h，汇总内存剩余最少的 3 台节点。

> 对集群 `<CLUSTER_UUID>` 执行 uptime，给出平均负载最高的 3 台节点。

### 4.8 指定单节点执行（target=node）

提示词：

> 只在节点 `<NODE_HOSTNAME>` 上执行 df_h。请调用 run_cluster_command，command_key=df_h，target=node，node_hostname=`<NODE_HOSTNAME>`。

期望：

- `results` 只有 1 条

### 4.9 负向：不支持的 command_key

提示词：

> 对集群 `<CLUSTER_UUID>` 执行 run_cluster_command，command_key=netstat_listen。

期望：

- 工具返回 `unsupported_command_key`，模型应解释目前只支持白名单键值

## 5. 集群启停：start_cluster / stop_cluster

### 5.1 启动

提示词：

> 请启动集群 `<CLUSTER_UUID>`（调用 start_cluster）。启动后再调用 run_cluster_command 的 jps 进行验证，并给出结论。

期望：

- 工具调用顺序：start_cluster → run_cluster_command(jps)

### 5.2 停止

提示词：

> 请停止集群 `<CLUSTER_UUID>`（调用 stop_cluster）。停止后再调用 run_cluster_command 的 jps 进行验证，并给出结论。

期望：

- 工具调用顺序：stop_cluster → run_cluster_command(jps)

### 5.3 负向：集群 UUID 不存在

提示词：

> 请启动集群 `00000000-0000-0000-0000-000000000000`。

期望：

- 工具返回 `cluster_not_found`，模型提示检查 UUID 与权限

## 6. 联网搜索：web_search

### 6.1 查错误码/异常解释

提示词：

> 我看到报错 “StandbyException: Operation category READ is not supported in state standby”。请调用 web_search 查一下这类异常常见原因和处理方式，并结合 Hadoop 场景给出建议。

期望：

- 工具返回 results（title/href/body/full_content），模型整合为中文结论

