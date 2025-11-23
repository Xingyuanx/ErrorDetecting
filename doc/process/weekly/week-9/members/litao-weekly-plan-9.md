# 第九周个人学习总结

## 本周概述
本周围绕“Hadoop简单项目实战与集群故障分析”开展学习，基于第八周Flume采集到HDFS的日志数据，完成了Hadoop MapReduce简单项目的开发、部署与运行，系统梳理了Hadoop集群（1Master+4Slave）常见故障类型，掌握故障排查思路与解决方案，提升了Hadoop集群实操与问题处理能力。

## 每日进展与成果

### 周日：项目需求梳理与环境准备
- 明确项目目标：基于Flume采集至HDFS的电商日志数据（路径`/flume/logs/%Y-%m-%d/%H/`），开发MapReduce项目实现“用户访问量统计”（按用户ID统计访问次数）与“页面访问Top10统计”。
- 梳理项目技术栈：确定使用Java开发MapReduce程序，依赖Hadoop 3.x API，使用Maven构建项目，最终打包为jar包提交至Hadoop集群运行。
- 环境校验与工具准备：确认Hadoop集群（HDFS、YARN）正常运行，本地开发环境（IDEA+Maven）配置完成，同步Hadoop集群`core-site.xml`、`hdfs-site.xml`至本地项目，确保开发环境与集群兼容。
- 数据预处理：通过`hdfs dfs -cat`查看日志数据格式，整理字段结构（用户ID、页面URL、访问时间、IP地址），排除无效数据（空字段、格式错误日志）。

### 周一：MapReduce项目开发与调试
- 完成项目架构设计：划分Mapper、Reducer、Driver三大核心模块，明确各模块职责（Mapper负责数据解析与kv输出，Reducer负责聚合统计，Driver负责任务配置与提交）。
- 编写核心代码：
  - Mapper类：解析日志行，提取用户ID/页面URL作为key，输出`<key, 1>`键值对；
  - Reducer类：接收相同key的value列表，求和后输出统计结果；
  - Driver类：配置Job名称、输入输出路径、Mapper/Reducer类、数据序列化格式，指定YARN资源参数（内存、CPU）。
- 本地调试：使用小批量日志数据作为输入，通过IDEA本地运行验证代码逻辑，解决数据解析异常、key-value输出格式错误等问题，确保统计结果准确。

### 周二：项目打包与集群运行
- 项目打包：通过Maven执行`clean package`命令，排除依赖冲突，生成可执行jar包（`hadoop-log-statistics.jar`），验证jar包完整性与兼容性。
- 上传jar包与运行：
  - 使用`scp`命令将jar包上传至Hadoop Master节点`/opt/hadoop/jobs`目录；
  - 执行提交命令：`hadoop jar hadoop-log-statistics.jar com.example.LogStatisticsDriver /flume/logs/2025-11-10/ /output/log-statistics/2025-11-10`；
  - 监控任务运行：通过YARN WebUI（8088端口）查看任务状态，确认Map/Reduce阶段正常执行，无资源不足、任务失败等问题。
- 结果验证：任务完成后，通过`hdfs dfs -cat /output/log-statistics/2025-11-10/part-r-00000`查看统计结果，确认用户访问量与页面Top10数据准确，符合预期。

### 周三：Hadoop集群常见故障类型梳理
- 系统梳理Hadoop核心组件故障分类：
  - HDFS相关：DataNode节点下线、NameNode单点故障、数据块损坏（Under-Replicated Blocks）、HDFS写入权限不足；
  - YARN相关：ResourceManager启动失败、NodeManager离线、任务提交超时、容器内存溢出（Container killed）；
  - 网络与配置相关：节点网络不通、配置文件参数错误（如`core-site.xml`端口配置错误）、SSH免密登录失效。
- 收集故障排查工具与命令：整理`jps`、`hdfs dfsadmin -report`、`yarn node -list`、`hadoop logs -applicationId <appId>`、`hdfs fsck /`等核心命令，明确各命令适用场景。
- 搭建故障模拟环境：在测试环境（本地虚拟机）模拟DataNode下线、配置文件错误等场景，记录故障现象与日志特征（日志路径：`$HADOOP_HOME/logs`）。

### 周四：HDFS故障排查实战
- 实战排查DataNode节点下线故障：
  - 故障现象：`hdfs dfsadmin -report`显示1个Slave节点DataNode未启动，WebUI（9870）显示该节点状态为“Decommissioned”；
  - 排查过程：查看该节点DataNode日志（`hadoop-hdfs-datanode-xxx.log`），发现“端口被占用”错误，通过`netstat -tulpn | grep 50010`定位占用进程并终止；
  - 解决结果：重启DataNode服务（`hdfs --daemon start datanode`），节点重新上线，HDFS数据块自动复制补全。
- 处理数据块损坏故障：
  - 故障现象：`hdfs fsck /`检测到`/flume/logs/2025-11-10/09/part-00000`存在损坏块；
  - 排查过程：通过`hdfs fsck /flume/logs/2025-11-10/09/part-00000 -locations`查看块存储节点，确认其中1个节点数据块损坏；
  - 解决结果：删除损坏块（`hdfs dfs -rm /flume/logs/2025-11-10/09/part-00000`），重新运行Flume采集任务补全数据，后续配置HDFS块冗余度为3（`dfs.replication=3`）避免单点损坏。
- 解决HDFS写入权限问题：排查`Permission denied: user=flume, access=WRITE`异常，通过`hdfs dfs -chmod -R 775 /flume/logs`授权目录，配置`HADOOP_USER_NAME=hdfs`环境变量解决。

### 周五：YARN与集群整体故障排查
- 排查YARN ResourceManager启动失败：
  - 故障现象：执行`start-yarn.sh`后，`jps`未显示ResourceManager进程；
  - 排查过程：查看日志（`yarn-hadoop-resourcemanager-xxx.log`），发现“端口8032被占用”，定位到是残留进程导致；
  - 解决结果：终止残留进程，重启YARN服务（`stop-yarn.sh && start-yarn.sh`），ResourceManager正常启动。
- 处理任务提交超时故障：
  - 故障现象：MapReduce任务提交后长时间处于“ACCEPTED”状态，无法进入“RUNNING”；
  - 排查过程：通过YARN WebUI查看节点资源，发现2个Slave节点NodeManager离线，且剩余节点内存不足（`yarn.nodemanager.resource.memory-mb=2048`配置过小）；
  - 解决结果：重启离线NodeManager服务，调整YARN资源配置（`yarn.nodemanager.resource.memory-mb=4096`、`yarn.scheduler.minimum-allocation-mb=1024`），任务正常执行。
- 解决容器内存溢出问题：优化MapReduce任务配置（`mapreduce.map.memory.mb=2048`、`mapreduce.reduce.memory.mb=4096`），避免任务运行中容器被YARN杀死。

### 周六：项目复盘与故障处理文档整理
- 项目复盘：总结MapReduce项目开发与运行流程，分析优化点（如使用Combiner减少Shuffle阶段数据传输、调整Map/Reduce任务并行度提升效率）；
- 整理故障处理手册：编写《Hadoop集群常见故障排查指南》，包含12类常见故障（HDFS 5类、YARN 4类、网络配置3类），每类故障涵盖“故障现象、排查步骤、解决方案、预防措施”，附核心命令与日志路径；
- 优化集群稳定性配置：基于故障排查经验，调整Hadoop核心配置（如开启NameNode HA避免单点故障、配置YARN资源弹性分配、设置Flume与Hadoop日志滚动策略）；