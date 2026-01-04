# Hadoop 故障复现与修复全过程指南

本文档详细说明了如何手动复现 Hadoop 集群的常见故障，并提供了详细的修复步骤，以及智能体在这些场景下的自动化处理逻辑。

---

## 故障 1：NameNode 强制进入安全模式 (Safe Mode)

### 1.1 手动复现步骤
在 NameNode 节点上执行以下命令，强制集群进入安全模式：
```bash
# 进入安全模式
hdfs dfsadmin -safemode enter

# 验证状态（此时 HDFS 无法进行写入操作）
hdfs dfsadmin -safemode get
hdfs dfs -touchz /test_file  # 预期报错：Name node is in safe mode.
```

### 1.2 手动修复步骤
1.  **检查原因**: 确认是否有磁盘空间不足或数据块损坏。
    ```bash
    df -h
    hdfs fsck /
    ```
2.  **强制退出**: 如果确认数据安全，手动退出：
    ```bash
    hdfs dfsadmin -safemode leave
    ```

### 1.3 智能体自动化方案
- **检测**: 智能体调用 `execute_command("hdfs dfsadmin -safemode get")` 解析输出。
- **决策**: 若检测到 `Safe mode is ON`，智能体接着检查磁盘空间和 `fsck` 结果。
- **修复**: 若各项指标正常，智能体调用工具执行 `hdfs dfsadmin -safemode leave`。

---

## 故障 2：DataNode 进程异常停止

### 2.1 手动复现步骤
在任意 DataNode 节点上模拟进程崩溃：
```bash
# 找到 DataNode 进程并强杀
ps -ef | grep DataNode | grep -v grep | awk '{print $2}' | xargs kill -9

# 验证状态（在 NameNode Web UI 或通过命令行查看）
hdfs dfsadmin -report | grep "Live datanodes"
```

### 2.2 手动修复步骤
1.  **查看日志**: 定位死亡原因（如 OOM）。
    ```bash
    tail -n 100 $HADOOP_HOME/logs/hadoop-*-datanode-*.log
    ```
2.  **重启进程**:
    ```bash
    hdfs --daemon start datanode
    ```
3.  **确认恢复**:
    ```bash
    jps | grep DataNode
    ```

### 2.3 智能体自动化方案
- **检测**: 智能体通过 [metrics_collector.py](file:///home/devbox/project/backend/app/metrics_collector.py) 发现节点 `health_status` 变为 `dead`。
- **决策**: 智能体调用 `read_log` 查找关键字 `OutOfMemoryError` 或 `FATAL`。
- **修复**: 智能体调用 [ops_tools.py](file:///home/devbox/project/backend/app/services/ops_tools.py) 中的 `restart_service` 接口执行重启。

---

## 故障 3：ResourceManager 挂掉导致任务无法提交

### 3.1 手动复现步骤
在 ResourceManager 节点上停止服务：
```bash
# 停止 RM
yarn --daemon stop resourcemanager

# 验证（提交一个简单的任务会卡死或报错）
yarn jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar pi 1 1
```

### 3.2 手动修复步骤
1.  **检查端口**: 确认 8088 端口是否监听。
    ```bash
    netstat -tpln | grep 8088
    ```
2.  **启动服务**:
    ```bash
    yarn --daemon start resourcemanager
    ```

### 3.3 智能体自动化方案
- **检测**: 智能体调用 [ssh_probe.py](file:///home/devbox/project/backend/app/services/ssh_probe.py) 探测端口失败，或 API 返回 502。
- **决策**: 判定为管理进程缺失。
- **修复**: 智能体通过 [diagnosis_agent.py](file:///home/devbox/project/backend/app/agents/diagnosis_agent.py) 自动触发 `start_cluster` 或特定的 `manage_service` 工具。

---

## 总结：通用修复流水线

无论是哪种故障，智能体都遵循以下标准流水线：
1.  **告警触发**: 接收到 Prometheus 或数据库状态异常。
2.  **环境快照**: 自动运行 `jps`, `df -h`, `free -m` 收集当前节点“画像”。
3.  **日志钻取**: 使用 `grep -E "ERROR|FATAL|Exception"` 在最近 5 分钟日志中搜索。
4.  **执行修复**: 调用预定义的运维脚本。
5.  **健康检查**: 修复后持续观察 1 分钟，确保进程没有再次崩溃。
