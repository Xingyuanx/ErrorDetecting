# 第十周个人周总结

## 核心目标达成情况
已基于Flume实现Hadoop集群日志（NameNode/DataNode/YARN等组件）的“全量+实时”采集，完成采集方案设计、多场景适配、性能优化及高可用验证，实现全量历史日志无遗漏、实时日志低延迟（≤30秒）写入HDFS，核心目标已达成。


## 每日进展与成果

### 周日：日志梳理与采集方案设计
- 完成Hadoop集群日志类型全面梳理：明确NameNode（元数据操作日志）、DataNode（磁盘IO日志）、YARN（ResourceManager/NodeManager日志）等组件的日志路径、格式（.log/.out）及轮转规则（按大小/时间轮转）。
- 确定Flume采集技术方案：全量采集采用Spooling Directory Source（支持断点续传+去重），实时采集采用Taildir Source（适配日志轮转+断点续传）；对比验证File Channel在高并发场景下稳定性优于Memory Channel。
- 完成“分布式采集+集中式聚合”架构设计：明确各节点采集Agent→聚合Agent→HDFS的数据流转路径，确定按“组件类型+日期+小时”分区策略，选用Snappy压缩格式，绘制架构流程图。
- 梳理并预判关键技术难点：形成日志轮转处理、大文件读取优化、多Agent数据冲突规避、网络波动应对等解决方案，整理Flume核心参数优化清单（如Channel容量、Sink批量提交大小）。


### 周一：全量采集方案实现与测试
- 完成全量采集Agent配置：在conf目录创建`full_log_collect.conf`，配置Spooling Directory Source（指定日志源目录、文件后缀过滤、完成标识）、File Channel（避免内存溢出）及HDFS Sink（存储路径`/hdfs/logs/full/%component%/%Y-%m-%d`）。
- 解决全量采集关键问题：通过`fileSuffix=".COMPLETED"`标记已采集文件，`deletePolicy="never"`保留源日志，`fileHeader=true`添加文件标识，避免重复采集。
- 验证全量采集功能：以20GB NameNode历史日志为样本，启动Agent后通过HDFS命令验证数据完整性（文件数、大小与源日志一致）。
- 优化采集效率：调整Channel容量（`capacity=100000`）、Sink批量提交大小（`hdfs.batchSize=1000`），解决大文件读取卡顿问题，全量采集速率稳定在≥30MB/s。


### 周二：实时采集方案优化与场景适配
- 完成实时采集Agent配置：创建`realtime_log_collect.conf`，支持多目录监控（nn/dn/yarn日志目录），配置`fileHeader=true`（标记来源组件）、`pollInterval=1000`（1秒监控间隔），适配日志轮转（.log→.log.1→.log.2）场景。
- 实现实时断点续传：启用Taildir Source的`positionFile`参数（路径`/var/flume/position/realtime.pos`），测试验证Agent重启后可从断点继续采集，无数据丢失。
- 控制实时采集延迟：通过模拟工具（10MB/min YARN日志生成）测试，日志生成与HDFS写入时间差稳定在30秒内，满足延迟要求。
- 适配异常场景：模拟日志文件删除/重命名、磁盘临时满等情况，验证Flume Agent可自动恢复采集，无数据丢失或重复。


### 周三：数据预处理与分区存储优化
- 完成数据预处理配置：通过RegexExtractorInterceptor提取日志时间戳、组件名称、日志级别（INFO/WARN/ERROR）等关键字段；使用StaticInterceptor添加集群标识；过滤无效日志（空行、调试日志）。
- 优化HDFS分区策略：基于提取字段配置HDFS Sink按“组件类型+日期+小时”分区（`hdfs.path=/hdfs/logs/realtime/%component%/%Y-%m-%d/%H`），启用`hdfs.round=true`实现时间对齐。
- 启用压缩与滚动优化：配置HDFS Sink使用Snappy压缩（`hdfs.compression.codec=org.apache.hadoop.io.compress.SnappyCodec`），设置滚动策略（128MB/15分钟/1000个文件，满足任一条件滚动）。
- 验证存储效果：HDFS分区目录结构符合预期，压缩文件解压后数据完整，无效日志占比≤0.1%，预处理规则生效。


### 周四：多Agent部署与负载均衡配置
- 完成分布式Agent部署：在Hadoop集群所有节点（master+slave1+slave2）部署Flume采集Agent，同步全量/实时配置文件，并按节点角色（主/从节点）适配日志目录监控范围。
- 实现聚合采集架构：在master节点部署聚合Agent，各采集Agent通过Avro Sink将数据发送至聚合Agent的Avro Source，配置Channel Selector实现按组件类型分流。
- 配置负载均衡与故障转移：使用Load Balancing Sink Processor，指定多个聚合Agent地址，启用failover机制（`maxFailoverAttempts=3`），确保单个聚合Agent故障时自动切换。
- 验证多节点稳定性：模拟峰值场景（所有节点同时生成日志），监控显示各采集Agent进程稳定，聚合Agent负载均衡效果良好，无数据堆积。


### 周五：性能压测与高可用验证
- 完成性能压测：模拟高并发场景（100MB/min日志吞吐量），持续2小时测试，关键指标达标（采集延迟≤25秒，HDFS写入吞吐量≥100MB/min，Channel队列无堆积）。
- 优化性能瓶颈：针对测试中出现的Channel短暂堵塞，调整file channel的`transactionCapacity`参数；优化HDFS Sink的`hdfs.rollInterval`及批量提交参数，提升写入效率；启用传输压缩缓解网络压力。
- 验证高可用：模拟slave1节点Agent宕机、master聚合Agent故障，故障期间数据无丢失，恢复后自动续传，全链路高可用验证通过。
- 完成兼容性测试：适配日志轮转（1GB大小轮转、按天轮转）及logrotate切割场景，无日志遗漏或重复采集。


### 周六：监控配置、文档整理与总结规划
- 配置监控告警：启用Flume JMX监控（通过`flume-env.sh`添加JMX参数），对接Ganglia/Zabbix系统，设置关键指标告警（Agent进程Down、Channel堆积超阈值、延迟超30秒）。
- 完成端到端联调：执行“全量历史日志导入+实时日志采集”全流程验证，数据从生成到HDFS存储的完整性、时效性均符合预期（全量无遗漏，实时延迟≤30秒）。
- 总结与规划：复盘本周计划全量完成，无未完成任务；提炼Flume“全量+实时”采集关键要点（场景适配、性能优化、高可用设计）；规划后续方向（日志脱敏、异常日志实时告警）。


## 总结
本周顺利完成基于Flume的Hadoop集群日志“全量+实时”采集方案设计与落地，通过多场景适配、性能优化及高可用验证，确保了日志数据的完整性（全量无遗漏）和时效性（实时延迟≤30秒），为后续日志分析奠定了数据基础。