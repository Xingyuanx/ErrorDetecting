# 故障检测系统ER图设计说明

## 1. ER图概述

### 1.1 设计目标
本ER图设计旨在为故障检测系统提供完整的数据模型，支持：
- Hadoop集群故障检测与自动修复
- 日志收集、存储和分析
- 用户权限管理和操作审计
- 系统配置和告警规则管理

### 1.2 建模工具
- **推荐工具**: PowerDesigner 16.5+
- **模型类型**: 概念数据模型(CDM) → 逻辑数据模型(LDM) → 物理数据模型(PDM)
- **数据库**: MySQL 8.0+

## 2. 实体设计

### 2.1 核心业务实体

#### 实体1: 故障记录 (FaultRecord)
**实体说明**: 系统检测到的故障信息
**主要属性**:
- fault_id (故障标识) - 主标识符
- fault_type (故障类型)
- fault_level (故障级别)
- title (故障标题)
- description (故障描述)
- status (处理状态)
- created_at (创建时间)
- resolved_at (解决时间)

**业务规则**:
- 每个故障必须有唯一的fault_id
- 故障级别分为: low, medium, high, critical
- 状态流转: detected → analyzing → repairing → resolved/failed

#### 实体2: 执行日志 (ExecutionLog)
**实体说明**: 自动修复脚本的执行记录
**主要属性**:
- exec_id (执行标识) - 主标识符
- command_type (命令类型)
- command_content (命令内容)
- execution_status (执行状态)
- start_time (开始时间)
- end_time (结束时间)
- exit_code (退出码)

**业务规则**:
- 每次执行必须关联一个故障记录
- 执行状态: pending → running → success/failed/timeout
- 高风险操作需要人工确认

#### 实体3: 集群状态 (ClusterStatus)
**实体说明**: Hadoop集群节点的状态信息
**主要属性**:
- node_id (节点标识) - 主标识符
- node_name (节点名称)
- ip_address (IP地址)
- node_role (节点角色)
- node_status (节点状态)
- cpu_usage (CPU使用率)
- memory_usage (内存使用率)
- disk_usage (磁盘使用率)
- health_score (健康评分)
- last_heartbeat (最后心跳)

**业务规则**:
- 节点角色: NameNode, DataNode, ResourceManager, NodeManager
- 节点状态: online, offline, maintenance, unknown
- 健康评分范围: 0-100

#### 实体4: 系统日志 (SystemLog)
**实体说明**: 从Flume采集的原始日志数据
**主要属性**:
- log_id (日志标识) - 主标识符
- timestamp (时间戳)
- host (主机名)
- service (服务名)
- log_level (日志级别)
- message (日志消息)
- processed (是否已处理)

**业务规则**:
- 日志级别: DEBUG, INFO, WARN, ERROR, FATAL
- 支持结构化和非结构化日志
- 日志保留期限: 90天

### 2.2 配置管理实体

#### 实体5: 系统配置 (SystemConfig)
**实体说明**: 系统运行参数配置
**主要属性**:
- config_key (配置键) - 主标识符
- config_value (配置值)
- config_type (配置类型)
- category (配置分类)
- is_active (是否启用)

**业务规则**:
- 配置键必须唯一
- 配置类型: string, int, boolean, json
- 支持配置的热更新

#### 实体6: 告警规则 (AlertRule)
**实体说明**: 系统告警规则定义
**主要属性**:
- rule_name (规则名称)
- rule_type (规则类型)
- metric_name (指标名称)
- condition_expr (条件表达式)
- threshold_value (阈值)
- severity (严重级别)
- is_enabled (是否启用)

**业务规则**:
- 规则类型: threshold, pattern, anomaly
- 严重级别: low, medium, high, critical
- 支持复杂的条件表达式

### 2.3 用户管理实体

#### 实体7: 用户 (User)
**实体说明**: 系统用户信息
**主要属性**:
- username (用户名) - 主标识符
- email (邮箱)
- password_hash (密码哈希)
- full_name (姓名)
- role (角色)
- department (部门)
- is_active (是否激活)
- last_login (最后登录)

**业务规则**:
- 用户名和邮箱必须唯一
- 角色类型: admin, operator, viewer
- 密码必须加密存储

#### 实体8: 操作审计 (AuditLog)
**实体说明**: 用户操作审计记录
**主要属性**:
- username (用户名)
- action (操作动作)
- resource_type (资源类型)
- resource_id (资源ID)
- ip_address (IP地址)
- created_at (操作时间)

**业务规则**:
- 记录所有重要操作
- 审计日志不可删除
- 保留期限: 1年

### 2.4 扩展实体

#### 实体9: 修复模板 (RepairTemplate)
**实体说明**: 预定义的修复脚本模板
**主要属性**:
- template_name (模板名称)
- fault_type (适用故障类型)
- script_content (脚本内容)
- risk_level (风险级别)
- parameters (参数定义)

#### 实体10: 通知配置 (NotificationConfig)
**实体说明**: 告警通知配置
**主要属性**:
- config_name (配置名称)
- notification_type (通知类型)
- trigger_conditions (触发条件)
- recipients (接收人)
- template_content (通知模板)

## 3. 实体关系设计

### 3.1 主要关系

#### 关系1: 故障记录 ↔ 执行日志 (1:N)
- **关系类型**: 一对多
- **关系说明**: 一个故障可能有多次修复执行记录
- **外键**: ExecutionLog.fault_id → FaultRecord.fault_id
- **约束**: 级联删除

#### 关系2: 用户 ↔ 操作审计 (1:N)
- **关系类型**: 一对多
- **关系说明**: 一个用户可能有多条操作审计记录
- **外键**: AuditLog.user_id → User.id
- **约束**: 设置为NULL（用户删除后保留审计记录）

#### 关系3: 故障记录 ↔ 系统日志 (N:M)
- **关系类型**: 多对多
- **关系说明**: 一个故障可能关联多条日志，一条日志可能关联多个故障
- **实现方式**: 通过JSON字段source_logs实现
- **备注**: 考虑性能，使用JSON而非关联表

#### 关系4: 集群状态 ↔ 故障记录 (1:N)
- **关系类型**: 一对多
- **关系说明**: 一个节点可能产生多个故障
- **实现方式**: 通过JSON字段affected_nodes实现
- **备注**: 支持一个故障影响多个节点

### 3.2 弱实体关系

#### 关系5: 修复模板 ↔ 执行日志 (1:N)
- **关系类型**: 一对多（弱关系）
- **关系说明**: 执行日志可能基于某个修复模板
- **实现方式**: 通过script_path字段关联
- **备注**: 不强制外键约束

#### 关系6: 告警规则 ↔ 故障记录 (1:N)
- **关系类型**: 一对多（弱关系）
- **关系说明**: 故障可能由某个告警规则触发
- **实现方式**: 通过业务逻辑关联
- **备注**: 不直接建立外键关系

## 4. PowerDesigner建模步骤

### 4.1 概念数据模型(CDM)创建

#### 步骤1: 创建实体
1. 打开PowerDesigner，新建概念数据模型
2. 使用Entity工具创建10个核心实体
3. 为每个实体添加标识符和属性
4. 设置属性的数据类型和约束

#### 步骤2: 建立关系
1. 使用Relationship工具连接相关实体
2. 设置关系的基数（1:1, 1:N, N:M）
3. 定义关系的角色名称
4. 设置关系的约束条件

#### 步骤3: 添加业务规则
1. 在实体上右键选择Properties
2. 在Business Rules标签页添加业务规则
3. 定义完整性约束和验证规则

### 4.2 逻辑数据模型(LDM)生成

#### 步骤1: CDM转换为LDM
1. 选择Tools → Generate Logical Data Model
2. 选择目标数据库类型（MySQL）
3. 配置转换选项和命名规则
4. 生成LDM

#### 步骤2: 优化逻辑模型
1. 检查表结构和字段定义
2. 优化数据类型和长度
3. 添加索引和约束
4. 验证外键关系

### 4.3 物理数据模型(PDM)生成

#### 步骤1: LDM转换为PDM
1. 选择Tools → Generate Physical Data Model
2. 选择MySQL 8.0数据库
3. 配置物理存储参数
4. 生成PDM

#### 步骤2: 物理优化
1. 设置表的存储引擎（InnoDB）
2. 配置字符集（utf8mb4）
3. 优化索引策略
4. 设置分区方案（如需要）

## 5. ER图布局建议

### 5.1 图形布局
```
核心业务区域（左上）:
┌─────────────────────────────────┐
│  FaultRecord ←→ ExecutionLog    │
│       ↕                        │
│  SystemLog   ←→ ClusterStatus   │
└─────────────────────────────────┘

配置管理区域（右上）:
┌─────────────────────────────────┐
│  SystemConfig                   │
│       ↕                        │
│  AlertRule                      │
└─────────────────────────────────┘

用户管理区域（左下）:
┌─────────────────────────────────┐
│  User ←→ AuditLog              │
└─────────────────────────────────┘

扩展功能区域（右下）:
┌─────────────────────────────────┐
│  RepairTemplate                 │
│       ↕                        │
│  NotificationConfig             │
└─────────────────────────────────┘
```

### 5.2 颜色编码建议
- **核心实体**: 蓝色系（#E3F2FD）
- **配置实体**: 绿色系（#E8F5E8）
- **用户实体**: 橙色系（#FFF3E0）
- **扩展实体**: 紫色系（#F3E5F5）

### 5.3 关系线样式
- **强关系**: 实线，带箭头
- **弱关系**: 虚线，带箭头
- **多对多**: 双向箭头
- **一对多**: 单向箭头

## 6. 数据完整性设计

### 6.1 实体完整性
- 每个实体必须有主键
- 主键不能为空且唯一
- 建议使用自增长ID作为代理键

### 6.2 参照完整性
- 外键必须引用存在的主键值
- 设置适当的级联操作
- 考虑孤儿记录的处理策略

### 6.3 域完整性
- 定义字段的数据类型和长度
- 设置NOT NULL约束
- 使用CHECK约束验证数据范围
- 定义枚举类型的有效值

### 6.4 用户定义完整性
- 业务规则约束
- 触发器实现复杂验证
- 存储过程封装业务逻辑

## 7. 性能优化考虑

### 7.1 索引设计
- 为外键字段创建索引
- 为频繁查询字段创建索引
- 考虑复合索引的使用
- 避免过多索引影响写入性能

### 7.2 分区策略
- system_logs表按时间分区
- audit_logs表按时间分区
- 大表考虑水平分区

### 7.3 数据类型优化
- 选择合适的数据类型长度
- 使用ENUM代替VARCHAR（固定值）
- JSON字段用于半结构化数据
- 时间字段使用TIMESTAMP

## 8. 文档生成

### 8.1 自动生成文档
1. 在PDM中选择Report → Generate Report
2. 选择HTML或RTF格式
3. 配置报告内容和样式
4. 生成完整的数据库设计文档

### 8.2 导出SQL脚本
1. 选择Database → Generate Database
2. 配置生成选项
3. 生成CREATE TABLE脚本
4. 包含索引、约束和初始数据

## 9. 版本控制

### 9.1 模型版本管理
- 使用PowerDesigner的版本控制功能
- 定期备份模型文件
- 记录每次修改的变更日志
- 建立模型审核流程

### 9.2 数据库变更管理
- 使用数据库迁移脚本
- 记录结构变更历史
- 建立回滚机制
- 测试环境先行验证

## 10. 最佳实践

### 10.1 命名规范
- 表名使用复数形式
- 字段名使用下划线分隔
- 外键字段以_id结尾
- 索引名以idx_开头

### 10.2 设计原则
- 遵循第三范式
- 避免冗余数据
- 考虑查询性能
- 保持模型简洁

### 10.3 维护建议
- 定期审查模型设计
- 根据业务变化调整结构
- 监控数据库性能
- 及时优化慢查询