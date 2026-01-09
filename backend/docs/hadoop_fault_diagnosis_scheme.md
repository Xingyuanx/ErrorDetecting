# Hadoop 常见故障诊断与智能体自动修复方案

本文档列出了 Hadoop 集群中常见的故障及其解决方案，并提供了一套基于 LLM 智能体的自动检测与修复编码方案。

## 一、 Hadoop 常见故障及解决方案

### 1. NameNode 处于安全模式 (Safe Mode)
- **故障现象**: HDFS 只能读取，无法写入或删除文件。
- **原因**: 集群启动时块汇报未达到阈值，或者磁盘空间不足、元数据损坏。
- **解决方案**:
    - 检查磁盘空间：`df -h`
    - 查看状态：`hdfs dfsadmin -safemode get`
    - 手动退出（确认安全后）：`hdfs dfsadmin -safemode leave`

### 2. DataNode 进程丢失或无法连接
- **故障现象**: 节点列表显示 DataNode 死亡，副本数不足。
- **原因**: 内存溢出 (OOM)、磁盘损坏、网络隔离、PID 文件丢失导致无法启动。
- **解决方案**:
    - 检查日志：`tail -n 200 /var/log/hadoop/hadoop-hadoop-datanode.log`
    - 检查磁盘：`fsck` 或查看 `dmesg`
    - 重启服务：`hdfs --daemon start datanode`

### 3. YARN 资源调度器 (ResourceManager) 响应慢/无法提交作业
- **故障现象**: 提交任务卡死，Web UI 无法访问。
- **原因**: 堆内存不足、Zookeeper 锁冲突、日志过多占满磁盘。
- **解决方案**:
    - 调整 JVM 参数：增加 `-Xmx`
    - 清理临时文件：`yarn cache -clean`
    - 重启 RM：`yarn --daemon start resourcemanager`

---

## 二、 智能体自动检测与修复编码方案

本方案基于项目现有的 [diagnosis_agent.py](file:///home/devbox/project/backend/app/agents/diagnosis_agent.py) 架构，通过 **Function Calling (工具调用)** 模式实现闭环。

### 1. 核心流程设计 (Observe-Think-Act)

1.  **观察 (Observe)**: 智能体通过监控告警或用户指令触发，调用 `read_log` 或 `execute_command` 获取集群现状。
2.  **思考 (Think)**: LLM 根据获取的上下文（日志片段、进程状态、磁盘水位）分析根因。
3.  **行动 (Act)**: LLM 选择最合适的修复工具（如 `fix_safemode`, `restart_service`）并执行。
4.  **验证 (Verify)**: 执行后再检查一次状态，确保修复成功。

### 2. 工具定义接口 (Tools Schema)

建议在 [ops_tools.py](file:///home/devbox/project/backend/app/services/ops_tools.py) 中扩展以下原子工具：

```python
def get_repair_tools():
    return [
        {
            "name": "check_hdfs_health",
            "description": "检查 HDFS 整体健康状态和安全模式",
            "parameters": {"type": "object", "properties": {}}
        },
        {
            "name": "manage_service",
            "description": "管理 Hadoop 服务（启动/停止/重启）",
            "parameters": {
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "节点主机名"},
                    "service": {"type": "string", "enum": ["datanode", "namenode", "resourcemanager"]},
                    "action": {"type": "string", "enum": ["start", "stop", "restart"]}
                },
                "required": ["node", "service", "action"]
            }
        },
        {
            "name": "fix_disk_space",
            "description": "清理指定目录下的日志或临时文件以释放空间",
            "parameters": {
                "type": "object",
                "properties": {
                    "node": {"type": "string"},
                    "path": {"type": "string", "description": "待清理的路径"}
                }
            }
        }
    ]
```

### 3. 智能体循环执行逻辑

在 [diagnosis_agent.py](file:///home/devbox/project/backend/app/agents/diagnosis_agent.py) 的 `run_diagnose_and_repair` 中，核心逻辑如下：

```python
async def run_diagnose_and_repair(db, operator, context, auto=True):
    # 1. 初始提示词
    messages = [{"role": "system", "content": "你是 Hadoop 专家。诊断并修复故障。"}]
    
    # 2. 循环诊断与修复
    for step in range(max_steps):
        # 让 LLM 决定下一步动作
        response = await llm.chat(messages, tools=tools)
        
        # 如果 LLM 给出结论而不再调用工具，则结束
        if not response.tool_calls:
            return {"status": "finished", "root_cause": response.content}
            
        # 3. 执行工具（例如重启服务）
        for tool in response.tool_calls:
            result = await execute_tool(tool) # 调用 SSHClient 执行命令
            messages.append({"role": "tool", "content": str(result), "name": tool.name})
            
    return {"status": "max_steps_reached"}
```

### 4. 关键实现细节
- **安全隔离**: 修复动作必须在 `SSHClient` 层面进行权限控制，避免 LLM 执行 `rm -rf /`。
- **状态感知**: 智能体应优先检查 `hdfs dfsadmin -report` 的结果，作为思考的基准数据。
- **上下文注入**: 在 `context` 中注入 [STATIC_NODE_CONFIG](file:///home/devbox/project/backend/app/ssh_utils.py)，让智能体知道有哪些 IP 和用户可以使用。
