# 第七周个人学习计划

## 学习目标
- 深入掌握Flume高级特性与性能调优方法，实现复杂场景数据采集链路
- 深化FastAPI框架应用，掌握异步接口、数据库集成及服务部署
- 独立完成Hadoop集群（5个虚拟机）部署与基础功能验证，理解分布式集群工作机制


## 详细计划

### 周日：基础回顾与环境准备
- **Flume学习**：
  - 回顾Flume核心组件（Agent、Source、Channel、Sink）协作原理
- **FastAPI学习**：
  - 复习FastAPI路由定义、参数处理及Pydantic数据模型基础
  - 搭建新的FastAPI项目结构（含路由分层、配置文件、依赖管理）
- **Hadoop集群部署准备**：
  - 确定集群节点规划
  - 检查硬件环境，安装CentOS 7系统
  - 下载Hadoop 和 JDK 安装包，上传至Master节点


### 周一：Flume高级特性与Hadoop单节点部署
- **Flume学习**：
  - 学习Flume拦截器高级用法：自定义拦截器开发（Java）、拦截器链配置
  - 实践：通过拦截器实现日志数据脱敏（手机号、邮箱隐藏）
- **FastAPI学习**：
  - 深入依赖注入：实现全局依赖（如数据库连接）、带参数的依赖函数
  - 学习安全认证：使用OAuth2+JWT实现接口权限控制
- **Hadoop部署**：
  - 完成Master节点JDK安装与环境变量配置（`JAVA_HOME`）
  - 安装Hadoop，配置`hadoop-env.sh`、`core-site.xml`基础参数
  - 启动Hadoop单节点模式，验证`hdfs dfs -ls /`命令执行成功


### 周二：Flume生态集成与Hadoop伪分布式部署
- **Flume学习**：
  - 学习Flume与生态组件集成：
    - Flume→Kafka→HDFS完整链路配置（解决数据积压问题）
    - Flume与HBase集成（使用AsyncHBase Sink写入数据）
  - 实践：采集本地日志→Kafka缓冲→HDFS存储的端到端测试
- **FastAPI学习**：
  - 实现数据库集成：使用SQLAlchemy连接MySQL，编写CRUD接口
  - 学习异步数据库操作：使用`asyncpg`连接PostgreSQL，开发异步接口
- **Hadoop部署**：
  - 配置Master节点伪分布式模式（`hdfs-site.xml`、`mapred-site.xml`、`yarn-site.xml`）
  - 格式化NameNode，启动HDFS与YARN服务，通过`jps`验证进程（NameNode、DataNode等）
  - 执行`hadoop jar`命令运行MapReduce示例程序（如WordCount）


### 周三：Flume性能调优与Hadoop集群配置
- **Flume学习**：
  - 性能调优参数：`batchSize`、`transactionCapacity`、线程池配置（`source.maxThreads`）
  - 实践：通过压测工具（如Flume Benchmark）验证调优效果，对比调优前后吞吐量
- **FastAPI学习**：
  - 接口文档优化：自定义Swagger UI描述、添加接口分组与标签
  - 学习服务部署：使用Gunicorn+Uvicorn部署FastAPI应用，配置进程数与端口
- **Hadoop部署**：
  - 配置Slave节点：在2个Slave节点安装JDK与Hadoop，同步Master节点配置文件
  - 配置SSH免密登录：实现Master到所有Slave节点的无密码登录
  - 编写`workers`文件，指定Slave节点主机名


### 周四：Flume实战案例与Hadoop集群启动
- **Flume学习**：
  - 实战案例：设计电商日志采集系统
    - Source：Spooling Directory Source监控日志目录
    - Channel：File Channel保证数据不丢失
    - Sink：分区写入HDFS（按日期+小时分区）
  - 编写启动脚本，实现Flume Agent后台运行与日志输出控制
- **FastAPI学习**：
  - 开发综合接口：实现用户注册→登录→数据查询的完整流程
  - 集成Redis：使用Redis缓存热点数据，减少数据库查询压力
- **Hadoop部署**：
  - 格式化Master节点NameNode，启动集群：`start-dfs.sh`、`start-yarn.sh`
  - 验证集群状态：通过`http://master:9870`查看HDFS WebUI，确认DataNode节点在线
  - 上传测试文件至HDFS，验证跨节点数据块存储（`hdfs dfs -ls /`、`hdfs fsck /`）


### 周五：FastAPI性能优化与Hadoop集群功能验证
- **Flume学习**：
  - 学习Flume监控：集成Ganglia/Ambari，监控Agent吞吐量、延迟指标
  - 故障排查：分析数据丢失/重复问题，总结排查流程（日志分析、配置校验）
- **FastAPI学习**：
  - 性能优化：使用`async/await`优化异步接口、添加接口限流（`slowapi`库）
  - 编写单元测试：使用`pytest`测试接口功能与异常处理
- **Hadoop部署**：
  - 验证MapReduce分布式执行：在集群运行WordCount程序，查看各节点任务分配
  - 测试HDFS高可用：模拟Slave节点下线，验证数据读写仍可用
  - 配置Hadoop历史服务器，查看任务执行日志


### 周六：综合项目整合与总结
- **综合实践**：
  - 整合三者：Flume采集电商日志→HDFS存储→FastAPI接口查询（按日期/用户ID筛选）
  - 验证流程：启动Flume Agent→生成测试日志→通过FastAPI查询HDFS中的日志数据
- **问题整理**：
  - 记录Flume配置中常见错误（如Channel与Sink参数不匹配）
  - 总结Hadoop集群部署坑点（SSH免密失败、防火墙拦截端口）
  - 整理FastAPI开发中异步与同步代码混合的注意事项
- **下周规划**：学习Hive数据仓库搭建，实现FastAPI与Hive的交互查询


## 学习资源
- Flume官方文档（性能调优章节）、《Flume权威指南》
- FastAPI官方文档（异步数据库、部署部分）、SQLAlchemy官方教程
- Hadoop官方部署指南、《Hadoop权威指南》集群配置章节
- B站：Hadoop 3.x集群部署实战视频、FastAPI企业级开发教程
- GitHub：Flume实战配置案例、FastAPI+MySQL开源项目