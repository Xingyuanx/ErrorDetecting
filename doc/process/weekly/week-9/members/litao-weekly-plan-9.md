# 第九周个人周计划

**核心目标**：完成Hadoop集群中HDFS存储配置的优化与验证，实现Flume的完整部署、配置及数据采集测试

**前置准备**：Hadoop基础环境（JDK、Hadoop安装包已就绪）、Flume安装包、集群节点信息文档、相关配置手册

## 周日：前期调研与环境梳理

- 1.梳理HDFS核心配置参数，重点标记与存储相关的配置项（如副本数、块大小、存储目录等），查阅官方文档确认参数优化建议

- 2.检查Hadoop基础环境完整性，验证SSH免密登录、JDK环境变量配置情况，清理集群节点上的冗余文件，确保环境干净

- 3.下载Flume对应版本安装包，核对与Hadoop版本的兼容性，整理Flume核心组件（Source、Channel、Sink）的工作机制资料

## 周一：HDFS存储配置方案设计与初步配置

- 1.结合实际业务场景（如数据量、读写频率）设计HDFS存储配置方案，确定副本数（默认3副本，根据节点数量调整）、块大小（大文件设为128M/256M）、元数据存储路径等关键参数

- 2.修改Hadoop核心配置文件，包括core-site.xml（配置HDFS主节点地址）、hdfs-site.xml（配置副本数、存储目录、元数据备份等），同步配置文件至集群所有节点

- 3.整理配置修改记录，标注每个参数的修改原因及预期效果，为后续验证做准备

## 周二：HDFS配置生效与功能验证

- 1.格式化HDFS文件系统（首次配置），启动HDFS集群（start-dfs.sh），通过jps命令检查NameNode、DataNode、SecondaryNameNode进程是否正常运行

- 2.通过HDFS命令行工具（hdfs dfs）执行基础操作，验证配置有效性：创建目录（mkdir）、上传文件（put）、查看文件信息（ls -h）、查看副本分布（fsck）

- 3.进行HDFS压力测试，上传不同大小文件（小文件集合、单个大文件），记录上传速度；模拟DataNode节点故障，检查副本自动修复功能是否正常；通过Web UI（50070端口）监控集群状态

- 4.分析测试结果，若存在性能瓶颈或配置问题，标记需调整的参数（如块大小、DataNode读写线程数等）

## 周三：HDFS配置优化与Flume部署准备

- 1.针对周二测试中发现的问题优化HDFS配置，如调整DataNode的磁盘IO参数、NameNode的元数据缓存参数等，重启集群后重新验证

- 2.在集群主节点解压Flume安装包，配置Flume环境变量（FLUME_HOME、PATH），修改flume-env.sh文件指定JDK路径

- 3.梳理Flume部署需求，确定数据采集场景（如采集本地日志文件至HDFS），设计Flume Agent配置方案（明确Source类型为exec/taildir，Sink类型为hdfs）

## 周四：Flume配置与部署

- 1.在Flume的conf目录下创建自定义Agent配置文件（如log2hdfs.conf），配置Source（监听目标日志文件）、Channel（使用memory或file通道）、Sink（指定HDFS存储路径及文件滚动策略）

- 2.检查Flume配置文件语法正确性（flume-ng agent -c conf -f conf/log2hdfs.conf -n a1 -Dflume.root.logger=INFO,console），排查配置错误（如路径不存在、权限不足等）

- 3.将配置好的Flume文件同步至需要部署Agent的节点，测试单节点Flume Agent启动命令，确保进程正常运行且无报错

- 4.编写Flume启动脚本，简化Agent启动与停止操作，记录配置过程中的问题及解决方法

## 周五：Flume数据采集功能测试与问题排查

- 1.启动Flume Agent，模拟日志文件生成（通过echo命令写入测试数据），通过HDFS命令行工具查看数据是否成功采集至目标目录，验证数据完整性

- 2.进行Flume稳定性测试，持续生成日志数据（30分钟以上），监控Flume进程状态、HDFS数据写入速度，检查是否出现数据丢失、重复采集等问题

- 3.排查测试中出现的问题，如通道堵塞则调整Channel容量参数，如数据写入延迟则优化Sink的批量提交参数，重启Agent后重新验证

## 周六：整体功能联调与总结复盘

- 1.进行HDFS与Flume整体联调，模拟完整业务场景（日志生成→Flume采集→HDFS存储），端到端验证数据流转的准确性与效率

- 2.整理本周工作成果，包括HDFS最终配置文件、Flume Agent配置文件、测试报告（含性能数据、问题及解决方案）

- 3.复盘本周计划执行情况，分析未完成任务（若有）的原因，总结HDFS配置与Flume部署的关键要点，为后续运维工作提供参考