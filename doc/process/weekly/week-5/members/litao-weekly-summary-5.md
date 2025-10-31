# 李涛第五周学习总结

## 一、学习目标达成情况
本周严格按照学习计划推进Spark相关知识学习，各项目标均顺利达成：
- 全面掌握Spark核心概念（RDD、DAG、宽/窄依赖等）及分布式架构原理
- 熟练运用Spark SQL进行数据查询与分析，包括基础操作与高级功能
- 深入理解Spark流处理机制，掌握DStream与Structured Streaming的使用方法
- 成功完成综合项目实践，构建完整的数据处理流水线

## 二、每日学习总结

### 周一
- 完成Spark RDD基础复习：巩固了RDD的创建方式（parallelize、textFile）、转换算子（map、filter、reduceByKey）与行动算子（collect、count）的特性及区别
- 系统学习Spark DataFrame API：掌握了从RDD、JSON、CSV等数据源创建DataFrame的方法，熟悉schema定义及select、filter、groupBy等常用操作
- 完成Spark SQL基础查询练习：通过实际数据集演练了SELECT、WHERE、GROUP BY等基础语法，实现了SQL与DataFrame API的灵活转换使用

### 周二
- 深入学习Spark SQL高级功能：重点掌握聚合函数（cube、rollup）的使用场景，理解临时视图与全局临时视图的区别及适用场景
- 掌握窗口函数与自定义UDF：清晰理解窗口函数的分区（PARTITION BY）、排序（ORDER BY）及窗口范围定义逻辑，成功编写并注册2个自定义UDF（字符串清洗、数值转换）
- 完成复杂数据分析案例：基于电商交易数据，实现了用户消费趋势、商品销售排行等多维度分析，验证了SQL高级功能的实用性

### 周三
- 学习Spark Streaming基础理论：理解流处理与批处理的核心差异，掌握DStream的创建方式（Socket、文件系统、Kafka对接）
- 掌握DStream核心操作：熟练运用transform、updateStateByKey、reduceByKeyAndWindow等算子处理实时数据
- 完成实时数据处理示例：基于Socket数据源搭建实时词频统计程序，验证窗口滑动机制与状态维护逻辑，确保数据处理准确性

### 周四
- 深入学习Structured Streaming：理解其基于DataFrame/Dataset的流处理模型，掌握流数据schema的自动推断与手动定义方法
- 掌握流处理窗口操作：实践滚动窗口（Tumbling Window）与滑动窗口（Sliding Window）在实时指标计算中的应用，解决时间对齐问题
- 完成流数据与静态数据结合分析：实现实时用户行为流数据与离线用户信息静态表的关联查询，动态更新用户活跃度标签

### 周五
- 学习Spark MLlib基础框架：了解MLlib的核心组件与数据类型（Vector、LabeledPoint），掌握Pipeline管道模型的构建流程
- 熟悉常用机器学习算法实现：学习逻辑回归（分类）、线性回归（回归）、K-Means（聚类）在Spark中的调用方式及参数配置
- 完成简单机器学习模型训练：基于用户历史消费数据，使用逻辑回归模型预测用户购买意愿，经测试模型准确率达81%

### 周末
- 完成综合项目实践：搭建"电商数据全流程处理系统"，涵盖离线数据清洗（Spark SQL）、实时数据接入（Structured Streaming + Kafka）、实时指标计算（窗口函数）、机器学习预测（MLlib）及结果存储（HDFS）全环节
- 系统总结本周学习内容：梳理核心知识点框架，整理关键API使用示例与注意事项
- 规划下周学习重点：聚焦Spark性能优化（Shuffle调优、内存配置）与多组件集成（HBase、Redis）

## 三、学习资源使用情况
- 《Spark权威指南》：重点研读第3章（RDD操作）、第5章（Spark SQL）、第8章（流处理）内容，辅助理解核心概念与原理
- Spark官方文档：查阅Structured Streaming编程指南、UDF注册方法、MLlib算法参数说明等细节内容
- Databricks社区教程：参考"实时数据分析最佳实践"案例，解决流数据与静态数据关联的技术难点
- GitHub示例项目：借鉴spark-examples仓库中的代码结构，优化综合项目的代码组织与异常处理逻辑

## 四、遇到的问题与解决方案
1. 问题：Spark SQL窗口函数中分区与排序逻辑混淆，导致计算结果异常  
   解决方案：通过绘制数据分区示意图，结合官方文档的窗口范围示例进行对比分析，明确分区是数据分组依据、排序是窗口内数据处理顺序的核心逻辑，最终通过小数据集分步调试验证逻辑正确性

2. 问题：Structured Streaming读取Kafka数据时出现重复消费现象  
   解决方案：检查Kafka消费者配置，将"startingOffsets"参数设为"earliest"，同时启用checkpoint机制持久化offset状态，成功解决数据重复消费问题

3. 问题：MLlib模型训练时因数据倾斜导致Executor内存溢出  
   解决方案：对训练数据进行预处理，通过随机拆分高频Key、提高shuffle并行度（spark.sql.shuffle.partitions）等方式平衡数据分布，最终顺利完成模型训练

## 五、本周成果总结
- 技能收获：熟练掌握Spark SQL数据分析技巧，具备独立设计流处理逻辑的能力，初步掌握Spark MLlib机器学习建模流程
- 项目成果：完成"电商数据全流程处理系统"综合项目，产出可运行代码（约750行）、测试报告及操作手册
- 文档产出：整理《Spark常用API速查表》《流处理问题排查手册》《综合项目设计说明》3份学习资料