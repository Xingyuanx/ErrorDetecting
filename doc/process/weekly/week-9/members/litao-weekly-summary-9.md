# 第九周个人周总结

**核心目标完成情况**：已完成Hadoop集群中HDFS存储配置的优化与验证，实现Flume的完整部署、配置及数据采集测试，各项功能符合预期目标

**前置准备完成情况**：Hadoop基础环境（JDK、Hadoop安装包）就绪，Flume安装包已下载并验证版本兼容性，集群节点信息文档及配置手册已整理归档

## 周日：前期调研与环境梳理

- 1.已完成HDFS核心存储配置参数梳理，标记副本数（dfs.replication）、块大小（dfs.blocksize）、存储目录（dfs.datanode.data.dir）等关键项，整理官方优化建议文档（附参考链接）

- 2.完成Hadoop基础环境检查：SSH免密登录在所有节点间验证通过，JDK环境变量（JAVA_HOME）配置正确，环境状态符合部署要求

- 3.已下载Flume 1.9.0版本安装包（与Hadoop 3.1.3兼容），整理Flume Source（exec/taildir）、Channel（memory/file）、Sink（hdfs）工作机制说明文档

## 周一：HDFS存储配置方案设计与初步配置

- 1.结合业务场景（日均数据量100GB，读写频率中等）确定配置方案：5节点集群、块大小设为256M（大文件为主），元数据存储路径分离至独立磁盘

- 2.已修改core-site.xml（配置fs.defaultFS为hdfs://master:9000）、hdfs-site.xml（配置副本数、存储目录等），通过scp命令同步配置文件至所有节点（slave1、slave2）

- 3.完成配置修改记录文档，详细标注每个参数修改原因（如副本数调整因节点数量限制）及预期效果（如块大小调整提升大文件读写效率）

## 周二：HDFS配置生效与功能验证

- 1.成功格式化HDFS文件系统（hdfs namenode -format），启动集群后jps验证：NameNode、DataNode、SecondaryNameNode进程在对应节点正常运行

- 2.基础操作验证通过：创建目录（hdfs dfs -mkdir /test）、上传文件（hdfs dfs -put test.txt /test）、查看信息（ls -h显示块大小256M）、fsck命令确认副本分布符合预期

- 3.压力测试结果：上传10GB单个文件耗时8分钟，1000个100KB小文件耗时12分钟；模拟slave1节点宕机后，副本在5分钟内自动修复；Web UI（50070）显示集群健康状态

- 4.发现DataNode磁盘IO效率偏低，标记需调整dfs.datanode.reader.count（读线程数）、dfs.datanode.writer.count（写线程数）参数

## 周三：HDFS配置优化与Flume部署准备

- 1.优化HDFS配置：将DataNode读写线程数从默认4调整为8，NameNode元数据缓存（dfs.namenode.fsnamesystem.cache.size）调大至100000，重启集群后IO性能提升约20%

- 2.已在主节点解压Flume安装包至/usr/local/flume，配置环境变量（FLUME_HOME=/usr/local/flume，PATH添加$FLUME_HOME/bin），修改flume-env.sh指定JDK路径（/usr/local/jdk1.8.0_341）

- 3.确定数据采集场景为“本地应用日志→HDFS”，设计Flume Agent方案：Source用taildir（实时监听日志变化）、Channel用file（避免内存溢出）、Sink用hdfs（按时间分区存储）

## 周四：Flume配置与部署

- 1.在conf目录创建log2hdfs.conf，完成配置：Source监听/var/log/app/*.log，Channel路径设为/var/flume/channel，Sink输出路径hdfs://master:9000/logs/%Y-%m-%d，滚动策略为128M或30分钟

- 2.通过命令验证配置语法正确（无报错输出），解决权限问题（为Flume用户赋予/var/log/app目录读权限、HDFS写入权限）

- 3.已将配置文件同步至slave1、slave2节点，单节点启动Agent成功（进程名为Application），日志无异常输出

- 4.编写Flume启动脚本（start-flume.sh）和停止脚本（stop-flume.sh），支持指定Agent名称启动，记录配置中解决的“Channel路径不存在”“HDFS权限拒绝”等问题

## 周五：Flume数据采集功能测试与问题排查

- 1.启动Flume Agent后，通过echo命令写入100条测试日志，HDFS目标目录成功生成数据文件，内容完整无丢失

- 2.稳定性测试：持续30分钟生成日志（约5GB），Flume进程稳定运行，HDFS写入速度约20MB/s，未出现数据丢失或重复

- 3.排查并解决Channel短暂堵塞问题：将file channel容量（capacity）从10000调至50000，解决写入延迟问题：将Sink批量提交大小（hdfs.batchSize）从100调至500，优化后性能符合预期

## 周六：整体功能联调与总结复盘

- 1.整体联调通过：模拟应用日志实时生成→Flume实时采集→HDFS按时间分区存储全流程通畅，数据从生成到HDFS可用平均延迟<30秒

- 2.整理本周成果：HDFS最终配置文件（core-site.xml、hdfs-site.xml）、Flume Agent配置文件（log2hdfs.conf）、测试报告（含性能指标、问题及解决方案清单）

- 3.复盘总结：所有计划任务均完成；关键要点包括“HDFS配置需结合节点数量调整副本数”“Flume Channel选择需考虑数据安全性与性能平衡”；后续需关注HDFS元数据增长情况及Flume监控告警配置