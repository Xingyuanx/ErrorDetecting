# 故障检测系统ER图设计说明

## 1. ER图概述

### 1.1 设计目标
本ER图设计旨在为故障检测系统提供完整的数据模型，支持：
- 多集群管理与故障检测
- 用户与集群的权限分离
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
- cluster_id (集群ID) - 外键
- fault_type (故障类型)
- fault_level (故障级别)
- title (故障标题)
- status (处理状态)

**业务规则**:
- 每个故障必须有唯一的fault_id
- 故障必须关联到一个集群

#### 实体2: 执行日志 (ExecutionLog)
**实体说明**: 自动修复脚本的执行记录
**主要属性**:
- exec_id (执行标识) - 主标识符
- command_type (命令类型)
- execution_status (执行状态)

**业务规则**:
- 每次执行必须关联一个故障记录

#### 实体3: 集群状态 (ClusterStatus)
**实体说明**: 集群各节点的状态信息
**主要属性**:
- node_id (节点标识) - 主标识符
- cluster_id (集群ID) - 外键
- node_name (节点名称)
- node_role (节点角色)
- node_status (节点状态)
- health_score (健康评分)

**业务规则**:
- 每个节点状态记录必须关联到一个集群

#### 实体4: 系统日志 (SystemLog)
**实体说明**: 从Flume采集的原始日志数据
**主要属性**:
- log_id (日志标识) - 主标识符
- cluster_id (集群ID) - 外键
- fault_id (关联故障ID)
- timestamp (时间戳)
- service (服务名)
- log_level (日志级别)

**业务规则**:
- 日志可以关联到特定集群和故障

### 2.2 配置管理与用户实体

#### 实体5: 集群 (Cluster)
**实体说明**: 用户管理的集群信息
**主要属性**:
- cluster_id (集群ID) - 主标识符
- cluster_name (集群名称)
- cluster_type (集群类型)
- description (描述)

**业务规则**:
- 集群名称必须唯一

#### 实体6: 用户 (User)
**实体说明**: 系统用户信息
**主要属性**:
- user_id (用户ID) - 主标识符
- username (用户名)
- email (邮箱)
- role (全局角色)

**业务规则**:
- 用户名和邮箱必须唯一
- 全局角色分为: admin, operator, viewer

#### 实体7: 用户集群映射 (UserClusterMapping)
**实体说明**: 用户和集群的多对多关系及角色定义
**主要属性**:
- user_id (用户ID) - 组合主标识符, 外键
- cluster_id (集群ID) - 组合主标识符, 外键
- role (集群角色)

**业务规则**:
- 定义用户在特定集群中的角色 (admin, operator, viewer)

#### 实体8: 操作审计 (AuditLog)
**实体说明**: 用户操作审计记录
**主要属性**:
- user_id (用户ID) - 外键
- cluster_id (集群ID) - 外键
- action (操作动作)
- resource_type (资源类型)

**业务规则**:
- 记录所有重要操作，并关联到用户和集群

#### 实体9: 应用配置 (AppConfiguration)
**实体说明**: 存储系统各类配置信息
**主要属性**:
- config_type (配置类型) - 组合主标识符
- config_key (配置键) - 组合主标识符
- config_value (配置值)

**业务规则**:
- config_type和config_key的组合必须唯一

### 2.3 扩展实体

#### 实体10: 修复模板 (RepairTemplate)
**实体说明**: 预定义的修复脚本模板
**主要属性**:
- template_name (模板名称)
- fault_type (适用故障类型)
- script_content (脚本内容)

## 3. 实体关系设计

### 3.1 核心关系 (多对多)

#### 关系1: 用户 ↔ 集群 (N:M)
- **关系类型**: 多对多
- **实现方式**: 通过`UserClusterMapping`中间表实现
- **关系说明**: 一个用户可以管理多个集群，一个集群也可以被多个用户管理
- **外键**:
  - UserClusterMapping.user_id → User.id
  - UserClusterMapping.cluster_id → Cluster.id

### 3.2 主要关系 (一对多)

#### 关系2: 集群 ↔ 故障记录 (1:N)
- **关系类型**: 一对多
- **外键**: FaultRecord.cluster_id → Cluster.id

#### 关系3: 集群 ↔ 集群状态 (1:N)
- **关系类型**: 一对多
- **外键**: ClusterStatus.cluster_id → Cluster.id

#### 关系4: 集群 ↔ 系统日志 (1:N)
- **关系类型**: 一对多
- **外键**: SystemLog.cluster_id → Cluster.id

#### 关系5: 集群 ↔ 操作审计 (1:N)
- **关系类型**: 一对多
- **外键**: AuditLog.cluster_id → Cluster.id

#### 关系6: 故障记录 ↔ 执行日志 (1:N)
- **关系类型**: 一对多
- **外键**: ExecutionLog.fault_id → FaultRecord.fault_id

#### 关系7: 用户 ↔ 操作审计 (1:N)
- **关系类型**: 一对多
- **外键**: AuditLog.user_id → User.id

#### 关系8: 故障记录 ↔ 系统日志 (1:N)
- **关系类型**: 一对多
- **外键**: SystemLog.fault_id → FaultRecord.fault_id

## 4. PowerDesigner建模步骤

### 4.1 概念数据模型(CDM)创建

#### 步骤1: 创建实体
1. 打开PowerDesigner，新建概念数据模型
2. 使用Entity工具创建10个实体
3. 为每个实体添加标识符和属性

#### 步骤2: 建立关系
1. 使用Relationship工具连接相关实体
2. **重点**: 创建User和Cluster之间的N:M关系，PowerDesigner会自动生成`UserClusterMapping`中间表
3. 设置其他1:N关系的基数和外键

### 4.2 逻辑与物理模型生成
(步骤与之前类似，确保在生成PDM时，所有外键和索引都已正确创建)

## 5. ER图布局建议

### 5.1 图形布局
```
中心区域（用户-集群关系）:
┌─────────────────────────────────┐
│      User ←- (N:M) -→ Cluster      │
│         (UserClusterMapping)      │
└─────────────────────────────────┘

集群关联实体（下方）:
┌─────────────────────────────────┐
│ Cluster --→ FaultRecord         │
│         --→ ClusterStatus       │
│         --→ SystemLog           │
│         --→ AuditLog            │
└─────────────────────────────────┘

其他关联实体（两侧）:
┌─────────────────────────────────┐
│ FaultRecord --→ ExecutionLog    │
│ User --→ AuditLog               │
└─────────────────────────────────┘

独立实体（顶部）:
┌─────────────────────────────────┐
│ AppConfiguration, RepairTemplate│
└─────────────────────────────────┘
```

### 5.2 颜色编码建议
- **核心实体**: 蓝色系 (FaultRecord, Cluster, User)
- **关联实体**: 绿色系 (ExecutionLog, ClusterStatus, SystemLog)
- **管理实体**: 灰色系 (AuditLog, AppConfiguration)
- **中间表**: 黄色系 (UserClusterMapping)

## 6. 数据完整性设计

### 6.1 参照完整性
- 确保所有外键都设置了正确的参照操作（如ON DELETE CASCADE或ON DELETE SET NULL）
- `UserClusterMapping`的`user_id`和`cluster_id`应设置为级联删除，确保主实体删除时，映射关系也被清理

(其他完整性设计与之前类似)

## 7. 性能优化考虑

### 7.1 索引设计
- 为所有外键字段创建索引，特别是`cluster_id`和`user_id`
- `UserClusterMapping`表的主键是`(user_id, cluster_id)`复合键，这本身就是一个高效的索引
- 考虑在`SystemLog`和`AuditLog`上创建基于`(cluster_id, created_at)`的复合索引，以优化按集群和时间范围的查询

(其他性能优化考虑与之前类似)

(8, 9, 10节内容与之前版本基本保持一致，仅需确保命名规范和设计原则覆盖到新表即可)