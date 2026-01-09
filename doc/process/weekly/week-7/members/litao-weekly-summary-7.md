# 第七周个人学习总结

## 学习目标达成情况
- 已掌握Flume高级特性（拦截器、生态集成）及性能调优方法，能独立设计复杂数据采集链路
- 深化FastAPI应用能力，熟练掌握异步接口开发、数据库集成及服务部署流程
- 成功完成5节点Hadoop集群部署与功能验证，理解分布式集群工作机制


## 每日学习总结

### 周日：基础回顾与环境准备
- **Flume**：回顾了Agent、Source、Channel、Sink核心组件协作原理，梳理了组件间数据流转逻辑
- **FastAPI**：复习路由定义、参数处理及Pydantic模型，搭建了包含路由分层、配置文件、依赖管理的项目结构
- **Hadoop准备**：完成5节点集群规划，安装CentOS 7系统，上传Hadoop和JDK安装包至Master节点


### 周一：Flume高级特性与Hadoop单节点部署
- **Flume**：学习自定义拦截器开发（Java），实现了日志数据脱敏功能（对手机号、邮箱进行隐藏处理），掌握拦截器链配置方法
- **FastAPI**：掌握全局依赖注入（如数据库连接池）和带参数依赖函数的实现，通过OAuth2+JWT完成接口权限控制功能开发
- **Hadoop**：完成Master节点JDK安装与环境变量配置，成功安装Hadoop并配置`hadoop-env.sh`、`core-site.xml`，启动单节点模式，`hdfs dfs -ls /`命令执行正常


### 周二：Flume生态集成与Hadoop伪分布式部署
- **Flume**：完成Flume→Kafka→HDFS全链路配置（解决了数据积压问题），实现Flume与HBase集成（通过AsyncHBase Sink写入数据），成功完成本地日志→Kafka→HDFS的端到端测试
- **FastAPI**：使用SQLAlchemy连接MySQL并编写CRUD接口，通过`asyncpg`实现PostgreSQL异步操作，开发了3个异步接口示例
- **Hadoop**：配置Master节点伪分布式模式（`hdfs-site.xml`、`mapred-site.xml`、`yarn-site.xml`），格式化NameNode后成功启动HDFS与YARN服务，`jps`验证进程正常，运行WordCount示例程序成功


### 周三：Flume性能调优与Hadoop集群配置
- **Flume**：学习`batchSize`、`transactionCapacity`、`source.maxThreads`等性能参数调优方法，通过Flume Benchmark工具进行压测，调优后吞吐量提升约30%
- **FastAPI**：完成Swagger UI自定义描述与接口分组标签配置，使用Gunicorn+Uvicorn部署应用，测试不同进程数（2-4个）对性能的影响
- **Hadoop**：在4个Slave节点完成JDK与Hadoop安装，同步Master节点配置文件，实现Master到所有Slave节点的SSH免密登录，编写`workers`文件指定节点主机名


### 周四：Flume实战案例与Hadoop集群启动
- **Flume**：设计并实现电商日志采集系统（Spooling Directory Source监控日志目录+File Channel保证数据可靠性+按日期+小时分区写入HDFS），编写启动脚本实现Agent后台运行与日志输出控制
- **FastAPI**：开发用户注册→登录→数据查询完整流程接口，集成Redis缓存热点数据，减少数据库查询耗时约40%
- **Hadoop**：格式化Master节点NameNode，通过`start-dfs.sh`、`start-yarn.sh`启动集群，`http://master:9870` WebUI确认所有DataNode在线，上传测试文件验证跨节点数据块存储正常


### 周五：FastAPI性能优化与Hadoop集群功能验证
- **Flume**：学习Flume与Ganglia集成监控方法，掌握吞吐量、延迟指标查看方式，总结数据丢失/重复问题排查流程（日志分析→配置校验→组件状态检查）
- **FastAPI**：使用`async/await`优化3个核心异步接口，通过`slowapi`库实现接口限流，编写`pytest`单元测试（覆盖率85%）验证接口功能与异常处理
- **Hadoop**：在集群运行WordCount程序验证MapReduce分布式执行，模拟2个Slave节点下线后数据读写仍正常，配置历史服务器成功查看任务执行日志


### 周六：综合项目整合与总结
- **综合实践**：完成Flume采集电商日志→HDFS存储→FastAPI接口查询全流程整合，成功验证：启动Flume Agent→生成测试日志→通过FastAPI按日期/用户ID筛选查询HDFS日志数据
- **问题整理**：记录Flume配置中Channel与Sink参数不匹配导致的数据积压问题、Hadoop部署中SSH免密失败（权限配置错误）和防火墙拦截端口（需开放9000/8088等端口）问题、FastAPI异步与同步代码混合导致的性能瓶颈


## 主要收获
- 掌握Flume在复杂场景下的配置与调优，能独立设计高可靠、高吞吐的数据采集方案
- 具备FastAPI企业级开发能力，包括异步处理、数据库交互、缓存集成、服务部署全流程
- 理解Hadoop分布式集群工作原理，能独立完成集群部署、故障排查与功能验证