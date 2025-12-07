# 第十周个人周计划

**核心目标**：基于Flume实现Hadoop集群日志（NameNode/DataNode/YARN等组件日志）的“全量+实时”采集，完成采集方案设计、多场景适配、性能优化及高可用验证，确保全量历史日志无遗漏、实时日志低延迟（≤30秒）写入HDFS

**前置准备**：已部署的Hadoop集群与Flume环境（承接第九周成果）、Hadoop各组件日志路径清单（nn/dn/yarn日志目录）、Flume全量/实时采集技术文档、数据压缩工具（Snappy/Gzip）、Flume Interceptor/Channel Selector配置手册、集群节点权限配置文档

## 周日：日志梳理与采集方案设计

- 1.全面梳理Hadoop集群日志类型：分类整理NameNode（元数据操作日志）、DataNode（磁盘IO日志）、YARN（ResourceManager/NodeManager日志）、Hive/HBase（可选）等组件的日志路径、文件格式（.log/.out）、轮转规则（按大小/时间轮转）

- 2.调研Flume全量+实时采集技术方案：确认全量采集（历史日志）采用Spooling Directory Source（断点续传+避免重复），实时采集（新增日志）采用Taildir Source（支持日志轮转+断点续传），对比不同Channel（file/memory）在高并发场景下的稳定性

- 3.设计整体采集架构：确定“分布式采集+集中式聚合”模式（各节点部署采集Agent→聚合Agent→HDFS），明确数据流转路径、分区策略（按组件类型+日期+小时）、数据压缩格式（Snappy），绘制架构流程图

- 4.梳理关键技术难点：预判日志轮转、大文件全量读取、多Agent数据冲突、网络波动等场景的解决方案，整理Flume核心参数优化建议（如Channel容量、Sink批量提交大小）

## 周一：全量采集方案实现与测试

- 1.配置Flume全量采集Agent：在conf目录创建full_log_collect.conf，指定Spooling Directory Source（配置日志源目录、文件后缀过滤、完成标识后缀），搭配File Channel（避免内存溢出），HDFS Sink（指定全量数据存储路径/hdfs/logs/full/%component%/%Y-%m-%d）

- 2.处理全量采集关键问题：配置fileSuffix=".COMPLETED"标记已采集文件，启用deletePolicy="never"保留源日志，通过fileHeader=true添加文件标识，避免重复采集

- 3.测试全量采集功能：选取NameNode历史日志（约20GB）作为测试样本，启动Flume Agent执行全量导入，通过HDFS命令验证数据完整性（文件数、大小与源日志一致），记录采集吞吐量

- 4.优化全量采集效率：调整Channel容量（capacity=100000）、Sink批量提交大小（hdfs.batchSize=1000），解决大文件读取卡顿问题，确保全量采集速率≥30MB/s

## 周二：实时采集方案优化与场景适配

- 1.基于Taildir Source优化实时采集配置：创建realtime_log_collect.conf，配置多目录监控（同时监听nn/dn/yarn日志目录），设置fileHeader=true（标记日志来源组件）、pollInterval=1000（1秒监控一次文件变化），支持日志轮转（.log→.log.1→.log.2）场景适配

- 2.实现实时采集断点续传：启用Taildir Source的positionFile参数（指定断点记录文件路径/var/flume/position/realtime.pos），测试Agent重启后是否从断点继续采集，避免数据丢失

- 3.验证实时采集延迟：通过模拟工具持续生成YARN节点日志（10MB/min），记录日志生成时间与HDFS写入完成时间的差值，优化参数将延迟控制在30秒内

- 4.处理异常场景：模拟日志文件被删除/重命名、磁盘临时满等情况，验证Flume Agent是否自动恢复采集，无数据丢失或重复采集

## 周三：数据预处理与分区存储优化

- 1.配置Flume Interceptor实现数据预处理：使用RegexExtractorInterceptor提取日志中的时间戳、组件名称、日志级别（INFO/WARN/ERROR）等关键字段，通过StaticInterceptor添加集群标识标签，过滤无效日志（如空行、调试日志）

- 2.优化HDFS Sink分区策略：基于提取的关键字段，配置HDFS Sink按“组件类型+日期+小时”分区（hdfs.path=/hdfs/logs/realtime/%component%/%Y-%m-%d/%H），启用hdfs.round=true实现时间对齐

- 3.启用数据压缩与文件滚动优化：配置HDFS Sink使用Snappy压缩（hdfs.compression.codec=org.apache.hadoop.io.compress.SnappyCodec），设置滚动策略（128MB/15分钟/文件数1000，满足任一条件滚动）

- 4.验证预处理与存储效果：查看HDFS分区目录结构是否符合预期，解压压缩文件验证数据完整性，检查过滤规则是否生效（无效日志占比≤0.1%）

## 周四：多Agent部署与负载均衡配置

- 1.分布式Agent部署：在Hadoop集群所有节点（master+slave1+slave2）部署Flume采集Agent，同步全量/实时采集配置文件，按节点角色（主节点/从节点）适配日志目录监控范围

- 2.设计聚合采集架构：在master节点部署聚合Agent，各采集Agent通过Avro Sink将数据发送至聚合Agent的Avro Source，配置Channel Selector实现按组件类型分流处理

- 3.配置负载均衡与故障转移：使用Flume的Load Balancing Sink Processor，指定多个聚合Agent地址，启用failover机制（maxFailoverAttempts=3），确保单个聚合Agent故障时自动切换

- 4.测试多节点采集稳定性：在所有节点同时生成日志（模拟峰值场景），监控各采集Agent进程状态，验证聚合Agent的负载均衡效果，确保无数据堆积

## 周五：性能压测与高可用验证

- 1.开展性能压测：使用日志生成工具模拟高并发场景（100MB/min日志吞吐量），持续2小时测试，记录Flume采集延迟、HDFS写入吞吐量、Channel队列堆积情况等关键指标

- 2.排查并优化性能瓶颈：若出现Channel堵塞，调整file channel的transactionCapacity参数；若Sink写入缓慢，优化HDFS Sink的hdfs.rollInterval和批量提交参数；若网络传输瓶颈，启用数据压缩优化

- 3.高可用验证：模拟采集Agent节点宕机（手动停止slave1节点Agent）、聚合Agent故障（停止master节点聚合Agent），检查故障期间数据是否丢失、故障恢复后是否自动续传，验证全链路高可用

- 4.兼容性测试：验证日志轮转（按大小1GB轮转、按天轮转）、日志切割（logrotate工具）场景下的采集适配性，确保无日志遗漏或重复采集

## 周六：监控配置、文档整理与总结规划

- 1.配置Flume监控告警：启用Flume JMX监控（配置flume-env.sh添加JMX参数），对接Ganglia/Zabbix监控系统，设置关键指标告警（Agent进程Down、Channel堆积量超阈值、采集延迟超30秒）

- 2.整体联调验证：执行“全量历史日志导入+实时日志采集”端到端流程，验证数据从日志生成→Flume采集→预处理→HDFS存储的完整性、时效性，确保全量无遗漏、实时低延迟

- 3.整理技术文档：归档Flume全量/实时采集配置文件（full_log_collect.conf/realtime_log_collect.conf）、聚合Agent配置、监控告警配置，编写操作手册（Agent启动/停止/重启、故障排查步骤）

- 4.总结与规划：复盘本周计划执行情况，分析未完成任务（若有）的原因，总结Flume“全量+实时”采集的关键要点（如场景适配、性能优化、高可用设计），规划后续优化方向（如日志脱敏、异常日志告警）