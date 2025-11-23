# 第八周个人学习总结

## 本周概述
本周围绕“Flume在Hadoop集群的部署、集成与优化”开展学习，完成了从环境准备到全链路验证的全流程实践，成功实现Flume与Hadoop（HDFS、YARN）的稳定集成，掌握多场景数据采集链路配置方法，形成标准化部署流程与实战经验。


## 每日进展与成果

### 周日：部署前置准备与环境校验
- 完成Hadoop集群状态全面校验：通过`jps`、`hdfs dfsadmin -report`等命令及WebUI（9870、8088端口）确认HDFS、YARN服务正常，4个Slave节点均在线。
- 验证集群网络与权限：Master与Slave节点互ping通畅，SSH免密登录生效，开放Flume通信及Hadoop交互必要端口。
- 完成Flume部署前置准备：下载Flume 1.11.0（适配Hadoop 3.x），确认所有节点JDK 8环境一致，同步Hadoop客户端jar包；规划并创建`/opt/flume`部署目录及`/var/log/flume`日志路径，配置权限。
- 预准备配置文件：复制并重命名Flume默认配置模板，同步Hadoop的`core-site.xml`、`hdfs-site.xml`至Flume配置目录。


### 周一：Flume集群部署与基础配置
- 完成全节点Flume安装：在Master节点解压安装包，配置`FLUME_HOME`环境变量并同步至4个Slave节点，确保所有节点Flume环境一致。
- 配置`flume-env.sh`：指定与Hadoop一致的`JAVA_HOME`和`HADOOP_HOME`，根据节点硬件配置堆内存为2-4G。
- 实现基础Agent测试：编写`single-agent.conf`（Spooling Directory Source → File Channel → HDFS Sink），生成模拟日志测试，成功验证数据写入HDFS指定目录，基础链路通畅。


### 周二：HDFS Sink优化与多Agent部署
- 完成HDFS Sink参数深度配置：实现按`/flume/logs/%Y-%m-%d/%H/`分区写入，配置滚动策略（`rollInterval=3600`、`rollSize=134217728`、`rollCount=10000`）；通过调整`batchSize=1000`、`hdfs.round=true`解决小文件问题。
- 配置容错机制：指定HDFS写入用户，开启Sink重试（`sink.maxRetries=3`），设置`failureChannel`存储失败数据。
- 完成Slave节点多Agent部署：4个Slave节点分别配置Agent，实现“本地日志采集→统一HDFS存储”架构，并发写入测试验证数据无重复、无丢失，分区完整。


### 周三：多数据源集成与数据处理
- 适配多数据源采集：配置TCP Source监听44444端口，成功接收外部系统推送日志并写入HDFS；搭建“Flume→Kafka→Flume→HDFS”链路，解决高吞吐场景数据缓冲问题。
- 实现数据格式处理：通过TimestampInterceptor、HostInterceptor为数据添加时间戳和节点IP元数据；配置`hdfs.serializer=Text`及UTF-8编码，确保后续Hadoop计算可正常读取。


### 周四：性能测试与优化
- 完成性能压测：使用自定义Python脚本模拟500条/秒、1000条/秒、2000条/秒的日志压力，监控HDFS写入速率、Flume Channel队列及YARN资源占用。
- 实施针对性优化：Flume层面调整`channel.capacity=100000`、`transactionCapacity=1000`、`source.maxThreads=5`；Hadoop层面将HDFS块大小设为256M，优化YARN容器内存配置；清理网络防火墙冗余规则，提升传输效率。优化后2000条/秒场景下链路稳定无数据积压。


### 周五：问题排查与稳定性验证
- 解决常见问题：通过`hdfs dfs -chmod`授权目录及配置`HADOOP_USER_NAME`解决权限`Permission denied`问题；对比File Channel与Memory Channel特性，调整事务参数确保数据一致性；优化`hdfs.callTimeout=30000`解决连接超时问题。
- 完成24小时稳定性验证：模拟Slave节点下线、网络抖动等场景，重启Agent后实现断点续传；通过`hdfs fsck /`校验HDFS数据完整性，链路可靠性达标。


### 周六：文档整理与综合实战
- 输出标准化文档：编写《Flume在Hadoop集群部署手册》，包含环境准备、安装步骤、启动/停止脚本及常见问题解决方案；整理单Agent、多Agent、Kafka集成等可复用配置模板。
- 完成综合实战：搭建“电商日志→Slave Flume→Kafka→Master Flume→HDFS→MapReduce统计”全链路，生成真实场景日志验证全流程通畅，成功输出统计结果。


## 主要收获
1. 掌握Flume在Hadoop集群（1Master+4Slave）的标准化部署流程，理解版本兼容（Flume 1.11+适配Hadoop 3.x）及权限互通要点。
2. 熟练配置Flume与HDFS、YARN集成参数，能针对不同场景（本地日志、TCP流、Kafka中间件）设计采集链路。
3. 具备Flume-Hadoop链路性能优化能力，可通过调整Channel、Sink参数及Hadoop配置提升吞吐量与稳定性。
4. 积累部署问题排查经验，能快速定位并解决权限、数据一致性、连接超时等常见问题。


## 后续计划
下周将学习Hive数据仓库搭建，基于本周Flume采集到HDFS的日志数据，实现Hive表创建、数据加载与SQL查询，完成数据从采集到分析的全链路闭环。