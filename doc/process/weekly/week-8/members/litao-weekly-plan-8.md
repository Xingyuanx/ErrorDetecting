# 第八周个人学习计划

## 学习目标
- 完成Flume在Hadoop集群（1Master+4Slave）的全节点部署与环境适配，确保Flume与Hadoop版本兼容、权限互通
- 掌握Flume与Hadoop核心组件（HDFS、YARN）的集成配置，实现多场景数据采集链路（本地日志、TCP流等）向HDFS稳定写入
- 验证Flume-Hadoop集成链路的可靠性、吞吐量，解决部署与运行中的常见问题，形成标准化部署流程与配置模板

## 详细计划

### 周日：部署前置准备与环境校验
- **Hadoop集群状态确认**：
  - 通过命令行（`jps`、`hdfs dfsadmin -report`、`yarn node -list`）与WebUI（9870、8088端口）验证HDFS、YARN服务正常运行
  - 检查集群节点网络连通性（Master与Slave互ping、SSH免密登录有效性），开放必要端口（Flume通信端口、HDFS/YARN交互端口）
- **Flume部署准备**：
  - 确认Flume与Hadoop版本兼容性（优先选择Flume 1.11+适配Hadoop 3.x），下载对应Flume安装包
  - 梳理Flume依赖项：确保所有节点JDK版本与Hadoop一致（推荐JDK 8），准备Hadoop客户端jar包（适配集群Hadoop版本）
  - 规划Flume部署目录（统一为`/opt/flume`）、日志存储路径（`/var/log/flume`），提前创建并配置权限
- **配置文件预准备**：
  - 复制Flume默认配置模板（`flume-env.sh.template`、`flume-conf.properties.template`），修改文件名备用
  - 整理Hadoop核心配置文件（`core-site.xml`、`hdfs-site.xml`），计划同步至Flume配置目录以实现环境感知

### 周一：Flume集群全节点部署与基础配置
- **Flume安装与环境配置**：
  - 将Flume安装包上传至Hadoop Master节点，解压并配置环境变量（`FLUME_HOME`、`PATH`），同步至所有Slave节点
  - 编辑`flume-env.sh`：指定`JAVA_HOME`（与Hadoop一致）、`HADOOP_HOME`，配置Flume堆内存（根据节点硬件调整，推荐2-4G）
  - 同步Hadoop配置：将Master节点`$HADOOP_HOME/etc/hadoop`下的`core-site.xml`、`hdfs-site.xml`复制到`$FLUME_HOME/conf`目录，确保Flume识别Hadoop集群
- **基础Agent配置与本地测试**：
  - 在Master节点编写简单Flume配置（`single-agent.conf`）：Source（Spooling Directory）→Channel（File Channel）→Sink（HDFS Sink）
  - 测试本地采集链路：创建测试日志目录，生成模拟日志，启动Flume Agent（`flume-ng agent -n a1 -c conf -f single-agent.conf`），验证数据成功写入HDFS指定目录

### 周二：Flume-HDFS Sink深度配置与多Agent部署
- **HDFS Sink核心参数优化**：
  - 配置HDFS分区写入：按日期（`%Y-%m-%d`）+小时（`%H`）设计输出路径（如`/flume/logs/%Y-%m-%d/%H/`），设置文件滚动策略（`rollInterval`、`rollSize`、`rollCount`）
  - 解决小文件问题：调整`batchSize`（批量写入条数）、`hdfs.round`（时间对齐）参数，避免HDFS产生大量小文件
  - 配置权限与容错：指定HDFS写入用户（`hdfs.user`），开启Sink重试机制（`sink.maxRetries`），设置死信队列（`failureChannel`）存储失败数据
- **Slave节点Flume Agent部署**：
  - 在4个Slave节点分别编写Agent配置，实现"多Source采集+统一HDFS存储"架构（Slave节点采集本地日志，统一写入Master管理的HDFS集群）
  - 测试多Agent并发写入：启动所有Slave节点Flume Agent，生成海量模拟日志，验证HDFS数据分区完整、无重复、无丢失

### 周三：Flume与Hadoop生态集成扩展
- **多数据源采集适配**：
  - 配置TCP Source：实现Flume Agent监听指定端口（如44444），接收外部系统推送的日志数据，写入HDFS
  - 集成Kafka作为中间件：搭建"Flume→Kafka→Flume→HDFS"链路（Slave节点Flume采集日志写入Kafka，Master节点Flume消费Kafka数据写入HDFS），解决高吞吐场景下的数据缓冲问题
- **数据格式处理与转换**：
  - 使用Flume拦截器（TimestampInterceptor、HostInterceptor）为采集数据添加时间戳、节点IP等元数据
  - 配置Flume序列化器（`hdfs.serializer=Text`），指定数据编码格式（UTF-8），确保Hadoop后续计算（MapReduce、Hive）可正常读取

### 周四：Flume-Hadoop链路性能测试与优化
- **性能压测与瓶颈分析**：
  - 使用Flume Benchmark工具（或自定义Python脚本）生成不同压力的日志数据（500条/秒、1000条/秒、2000条/秒）
  - 监控链路指标：通过HDFS WebUI查看写入速率，通过Flume日志分析Channel满队列情况、Sink写入延迟，通过YARN查看集群资源占用
- **针对性优化**：
  - Flume层面：调整Channel容量（`channel.capacity`）、事务大小（`channel.transactionCapacity`），增加Source线程数（`source.maxThreads`）
  - Hadoop层面：调整HDFS块大小（`dfs.blocksize`，推荐128M/256M），优化YARN容器内存（`yarn.nodemanager.resource.memory-mb`），避免资源不足导致写入超时
  - 网络层面：检查节点间网络带宽，关闭不必要的防火墙规则，优化HDFS数据传输缓冲区（`io.file.buffer.size`）

### 周五：部署问题排查与链路稳定性验证
- **常见问题排查与解决**：
  - 权限问题：排查`Permission denied`异常，通过`hdfs dfs -chmod`授权目录、配置`HADOOP_USER_NAME`环境变量解决
  - 数据丢失/重复：分析Flume Channel类型选择（File Channel适合高可靠场景，Memory Channel适合高吞吐场景），调整事务参数确保数据一致性
  - 连接超时：排查Hadoop服务端口占用、网络连通性，优化Flume Sink连接超时参数（`hdfs.callTimeout`）
- **稳定性长时间验证**：
  - 持续运行Flume-Hadoop链路24小时，模拟节点临时下线（关闭1个Slave节点Agent）、网络抖动（短暂断开网络）等场景
  - 验证故障恢复能力：重启故障节点Agent，检查是否能断点续传数据；通过`hdfs fsck /`校验HDFS数据完整性

### 周六：部署文档整理与综合实战
- **标准化文档与模板整理**：
  - 编写《Flume在Hadoop集群部署手册》，包含环境准备、安装步骤、配置模板、启动/停止脚本、常见问题解决方案
  - 整理可复用配置文件：单Agent基础配置、多Agent分布式配置、Kafka集成配置、HDFS分区写入配置等
- **综合实战演练**：
  - 搭建完整业务链路：模拟电商系统日志→Slave节点Flume采集→Kafka缓冲→Master节点Flume消费→HDFS分区存储→MapReduce任务统计日志数据
  - 全流程验证：启动所有组件，生成真实场景日志，验证数据采集、传输、存储、计算全链路通畅，输出统计结果
- **下周规划**：学习Hive数据仓库搭建，基于Flume采集到HDFS的日志数据，实现Hive表创建、数据加载与SQL查询

## 学习资源
- Flume官方文档（HDFS Sink配置章节、性能优化指南）
- Hadoop官方文档（客户端配置、HDFS权限管理、YARN资源配置）
- 《Flume权威指南》Hadoop集成章节
- 博客：《Flume与Hadoop 3.x集成最佳实践》《Flume HDFS Sink参数优化详解》
- GitHub：Flume-Hadoop集成配置案例、Flume压测工具脚本
- B站：Hadoop集群Flume部署实战视频、Flume性能调优教程