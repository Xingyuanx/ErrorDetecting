# Hadoop Fault Detecting API 文档

## 项目概述

这是一个用于Hadoop故障检测的API服务，基于FastAPI框架开发。该服务提供了集群管理、节点监控、日志分析、故障检测等功能，帮助管理员实时监控和管理Hadoop集群。

## 技术栈

- **框架**: FastAPI
- **语言**: Python 3.13
- **依赖**: SQLAlchemy, asyncpg, python-dotenv, passlib, PyJWT, langchain, httpx, paramiko

## 目录结构

```
app/
├── agents/          # AI智能代理
├── deps/            # 依赖项
├── models/          # 数据库模型
├── routers/         # API路由
├── services/        # 业务逻辑
├── config.py        # 配置文件
├── db.py            # 数据库连接
├── log_collector.py # 日志收集器
├── log_reader.py    # 日志阅读器
├── main.py          # 应用入口
├── schemas.py       # 数据模型
├── ssh_utils.py     # SSH工具
└── __init__.py      # 包初始化
```

## API 路由概述

| 模块 | 路径前缀 | 功能描述 |
|------|----------|----------|
| health | /api/v1 | 健康检查 |
| auth | /api/v1 | 身份认证 |
| secure | /api/v1 | 安全相关 |
| clusters | /api/v1 | 集群管理 |
| nodes | /api/v1 | 节点管理 |
| metrics | /api/v1 | 指标监控 |
| users | /api/v1 | 用户管理 |
| hadoop_logs | /api/v1 | Hadoop日志管理 |
| faults | /api/v1 | 故障检测 |
| hadoop_exec_logs | /api/v1 | Hadoop执行日志 |
| ops | /api/v1 | 操作管理 |
| ai | /api/v1 | AI智能分析 |
| sys_exec_logs | /api/v1 | 系统操作日志 |

## 详细API文档

### 1. 健康检查 (health.py)

#### 接口列表

| 方法 | 路径 | 功能描述 | 认证要求 |
|------|------|----------|----------|
| GET | /health | 健康检查，包括数据库连接验证 | 否 |

#### 详细接口说明

##### GET /health

**功能描述**：
检查服务健康状态，同时验证数据库连接是否正常。

**请求参数**：
无

**响应格式**：
```json
{
  "status": "ok",
  "database": "connected"  // 或 "disconnected: 错误信息"
}
```

**响应示例**：
```json
{
  "status": "ok",
  "database": "connected"
}
```

**错误示例**：
```json
{
  "status": "ok",
  "database": "disconnected: connection refused"
}
```

### 2. 身份认证 (auth.py)

#### 接口列表

| 方法 | 路径 | 功能描述 | 认证要求 |
|------|------|----------|----------|
| POST | /user/login | 用户登录 | 否 |
| POST | /user/register | 用户注册 | 否 |
| GET | /user/me | 获取当前用户信息 | 是 |

#### 详细接口说明

##### POST /user/login

**功能描述**：
用户登录，验证用户名和密码，返回JWT令牌。

**请求体**：
```json
{
  "username": "string",
  "password": "string"
}
```

**请求示例**：
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**响应格式**：
```json
{
  "ok": true,
  "username": "string",
  "fullName": "string",
  "token": "string"
}
```

**响应示例**：
```json
{
  "ok": true,
  "username": "admin",
  "fullName": "admin",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**错误示例**：
```json
{
  "detail": "invalid_credentials"
}
```

##### POST /user/register

**功能描述**：
用户注册，创建新用户并返回JWT令牌。

**请求体**：
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "fullName": "string"
}
```

**请求示例**：
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "NewPass123",
  "fullName": "New User"
}
```

**验证规则**：
- 用户名：3-50个字符，以字母开头，支持字母/数字/下划线
- 邮箱：有效的邮箱格式
- 密码：至少8位，包含大小写字母和数字
- 姓名：2-100个字符

**响应格式**：
```json
{
  "ok": true,
  "username": "string",
  "fullName": "string",
  "token": "string"
}
```

**响应示例**：
```json
{
  "ok": true,
  "username": "newuser",
  "fullName": "New User",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**错误示例**：
```json
{
  "detail": {
    "errors": [
      {
        "field": "password",
        "code": "weak_password",
        "message": "密码至少8位，需包含大小写字母与数字"
      }
    ]
  }
}
```

##### GET /user/me

**功能描述**：
获取当前登录用户的信息。

**请求参数**：
无

**请求头**：
```
Authorization: Bearer {token}
```

**响应格式**：
```json
{
  "username": "string",
  "fullName": "string",
  "isActive": boolean
}
```

**响应示例**：
```json
{
  "username": "admin",
  "fullName": "admin",
  "isActive": true
}
```

### 3. 集群管理 (clusters.py)

#### 接口列表

| 方法 | 路径 | 功能描述 | 认证要求 |
|------|------|----------|----------|
| GET | /clusters | 获取当前用户可访问的集群列表 | 是 |
| POST | /clusters | 注册新集群并建立用户归属映射 | 是 |
| DELETE | /clusters/{uuid} | 注销指定集群并清理用户归属映射 | 是 |

#### 详细接口说明

##### GET /clusters

**功能描述**：
按当前用户归属返回其可访问的集群列表。

**请求参数**：
无

**请求头**：
```
Authorization: Bearer {token}
```

**响应格式**：
```json
{
  "clusters": [
    {
      "uuid": "string",
      "host": "string",
      "ip": "string",
      "count": 0,
      "health": "string"
    }
  ]
}
```

**响应示例**：
```json
{
  "clusters": [
    {
      "uuid": "123e4567-e89b-12d3-a456-426614174000",
      "host": "hadoop-master",
      "ip": "192.168.1.100",
      "count": 5,
      "health": "running"
    }
  ]
}
```

##### POST /clusters

**功能描述**：
注册一个新集群并建立当前用户的归属映射。

**请求头**：
```
Authorization: Bearer {token}
```

**请求体**：
```json
{
  "uuid": "string",
  "host": "string",
  "ip": "string",
  "count": 0,
  "health": "string"
}
```

**请求示例**：
```json
{
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "host": "hadoop-master",
  "ip": "192.168.1.100",
  "count": 5,
  "health": "running"
}
```

**响应格式**：
```json
{
  "ok": true
}
```

**错误示例**：
```json
{
  "detail": "not_allowed"
}
```

##### DELETE /clusters/{uuid}

**功能描述**：
注销指定集群，并清理用户归属映射。

**请求参数**：
- uuid: 集群的UUID（路径参数）

**请求头**：
```
Authorization: Bearer {token}
```

**响应格式**：
```json
{
  "ok": true
}
```

**错误示例**：
```json
{
  "detail": {
    "errors": [
      {
        "field": "uuid",
        "message": "UUID 格式不正确"
      }
    ]
  }
}
```

### 4. 节点管理 (nodes.py)

#### 接口列表

| 方法 | 路径 | 功能描述 | 认证要求 |
|------|------|----------|----------|
| GET | /nodes | 拉取指定集群的节点列表 | 是 |
| GET | /nodes/{name} | 查询节点详情 | 是 |

#### 详细接口说明

##### GET /nodes

**功能描述**：
拉取指定集群的节点列表。

**请求参数**：
- cluster: 集群UUID（查询参数，必填）

**请求头**：
```
Authorization: Bearer {token}
```

**响应格式**：
```json
{
  "nodes": [
    {
      "name": "string",
      "ip": "string",
      "status": "string",
      "cpu": "string",
      "mem": "string",
      "updated": "string"
    }
  ]
}
```

**响应示例**：
```json
{
  "nodes": [
    {
      "name": "hadoop-node1",
      "ip": "192.168.1.101",
      "status": "running",
      "cpu": "25%",
      "mem": "60%",
      "updated": "10分钟前"
    }
  ]
}
```

##### GET /nodes/{name}

**功能描述**：
查询指定节点的详细信息。

**请求参数**：
- name: 节点名称（路径参数，必填）

**请求头**：
```
Authorization: Bearer {token}
```

**响应格式**：
```json
{
  "name": "string",
  "metrics": {
    "cpu": "string",
    "mem": "string",
    "disk": "string",
    "status": "string",
    "ip": "string",
    "lastHeartbeat": "string"
  }
}
```

**响应示例**：
```json
{
  "name": "hadoop-node1",
  "metrics": {
    "cpu": "25%",
    "mem": "60%",
    "disk": "45%",
    "status": "running",
    "ip": "192.168.1.101",
    "lastHeartbeat": "2025-12-18T00:00:00+00:00"
  }
}
```

### 5. 指标监控 (metrics.py)

#### 接口列表

| 方法 | 路径 | 功能描述 | 认证要求 |
|------|------|----------|----------|
| GET | /metrics/cpu_trend | 获取指定集群的CPU使用率趋势数据 | 是 |
| GET | /metrics/memory_usage | 获取指定集群的内存使用情况 | 是 |
| GET | /metrics/cpu_trend_node | 获取指定节点的CPU使用率趋势数据 | 是 |
| GET | /metrics/memory_usage_node | 获取指定节点的内存使用情况 | 是 |

#### 详细接口说明

##### GET /metrics/cpu_trend

**功能描述**：
获取指定集群的CPU使用率趋势数据。

**请求参数**：
- cluster: 集群UUID（查询参数，必填）

**请求头**：
```
Authorization: Bearer {token}
```

**响应格式**：
```json
{
  "times": ["string"],
  "values": [0]
}
```

**响应示例**：
```json
{
  "times": ["00:00","04:00","08:00","12:00","16:00","20:00","24:00"],
  "values": [20, 25, 30, 35, 40, 35, 30]
}
```

##### GET /metrics/memory_usage

**功能描述**：
获取指定集群的内存使用情况（单位：百分比）。

**请求参数**：
- cluster: 集群UUID（查询参数，必填）

**请求头**：
```
Authorization: Bearer {token}
```

**响应格式**：
```json
{
  "used": 0.0,
  "free": 0.0
}
```

**响应示例**：
```json
{
  "used": 60.5,
  "free": 39.5
}
```

##### GET /metrics/cpu_trend_node

**功能描述**：
获取指定节点的CPU使用率趋势数据。

**请求参数**：
- cluster: 集群UUID（查询参数，必填）
- node: 节点名称（查询参数，必填）

**请求头**：
```
Authorization: Bearer {token}
```

**响应格式**：
```json
{
  "times": ["string"],
  "values": [0]
}
```

**响应示例**：
```json
{
  "times": ["00:00","04:00","08:00","12:00","16:00","20:00","24:00"],
  "values": [15, 20, 25, 30, 35, 30, 25]
}
```

##### GET /metrics/memory_usage_node

**功能描述**：
获取指定节点的内存使用情况（单位：百分比）。

**请求参数**：
- cluster: 集群UUID（查询参数，必填）
- node: 节点名称（查询参数，必填）

**请求头**：
```
Authorization: Bearer {token}
```

**响应格式**：
```json
{
  "used": 0.0,
  "free": 0.0
}
```

**响应示例**：
```json
{
  "used": 55.2,
  "free": 44.8
}
```

### 6. 故障检测 (faults.py)

#### 接口列表

| 方法 | 路径 | 功能描述 | 认证要求 |
|------|------|----------|----------|
| GET | /faults | 获取故障列表，支持筛选条件 | 是 |
| POST | /faults | 创建新故障（仅管理员/操作员） | 是 |
| PUT | /faults/{fid} | 更新故障信息（仅管理员/操作员） | 是 |
| DELETE | /faults/{fid} | 删除故障（仅管理员/操作员） | 是 |

#### 详细接口说明

##### GET /faults

**功能描述**：
获取故障列表，支持筛选条件。

**请求参数**：
- cluster: 集群UUID或名称（可选）
- node: 节点名称（可选）
- time_from: 开始时间（ISO格式，可选）
- page: 页码（默认1）
- size: 每页条数（默认10，1-100）

**请求头**：
```
Authorization: Bearer {token}
```

**响应格式**：
```json
{
  "items": [
    {
      "id": "string",
      "type": "string",
      "level": "string",
      "status": "string",
      "title": "string",
      "cluster": "string",
      "node": "string",
      "created": "string"
    }
  ],
  "total": 0
}
```

**响应示例**：
```json
{
  "items": [
    {
      "id": "fault-123",
      "type": "disk",
      "level": "error",
      "status": "active",
      "title": "磁盘空间不足",
      "cluster": "123e4567-e89b-12d3-a456-426614174000",
      "node": "hadoop-node1",
      "created": "2025-12-18T00:00:00+00:00"
    }
  ],
  "total": 1
}
```

##### POST /faults

**功能描述**：
创建新故障，仅管理员和操作员可使用。

**请求头**：
```
Authorization: Bearer {token}
```

**请求体**：
```json
{
  "id": "string",
  "type": "string",
  "level": "string",
  "status": "string",
  "title": "string",
  "cluster": "string",
  "node": "string",
  "created": "string"
}
```

**请求示例**：
```json
{
  "id": "fault-123",
  "type": "disk",
  "level": "error",
  "status": "active",
  "title": "磁盘空间不足",
  "cluster": "123e4567-e89b-12d3-a456-426614174000",
  "node": "hadoop-node1",
  "created": "2025-12-18T00:00:00+00:00"
}
```

**响应格式**：
```json
{
  "ok": true
}
```

**错误示例**：
```json
{
  "detail": "not_allowed"
}
```

##### PUT /faults/{fid}

**功能描述**：
更新故障信息，仅管理员和操作员可使用。

**请求参数**：
- fid: 故障ID（路径参数，必填）

**请求头**：
```
Authorization: Bearer {token}
```

**请求体**：
```json
{
  "status": "string",
  "title": "string"
}
```

**请求示例**：
```json
{
  "status": "resolved",
  "title": "磁盘空间不足已解决"
}
```

**响应格式**：
```json
{
  "ok": true
}
```

**错误示例**：
```json
{
  "detail": "not_found"
}
```

##### DELETE /faults/{fid}

**功能描述**：
删除故障，仅管理员和操作员可使用。

**请求参数**：
- fid: 故障ID（路径参数，必填）

**请求头**：
```
Authorization: Bearer {token}
```

**响应格式**：
```json
{
  "ok": true
}
```

**错误示例**：
```json
{
  "detail": "not_allowed"
}
```

### 7. Hadoop执行日志 (hadoop_exec_logs.py)

#### 接口列表

| 方法 | 路径 | 功能描述 | 认证要求 |
|------|------|----------|----------|
| GET | /exec-logs | 获取所有执行日志 | 是 |
| POST | /exec-logs | 创建新的执行日志 | 是 |
| PUT | /exec-logs/{log_id} | 更新执行日志 | 是 |
| DELETE | /exec-logs/{log_id} | 删除执行日志 | 是 |

#### 详细接口说明

##### GET /exec-logs

**功能描述**：
获取所有执行日志，按开始时间倒序排列。

**请求头**：
```
Authorization: Bearer {token}
```

**响应格式**：
```json
{
  "items": [
    {
      "id": 0,
      "from_user_id": 0,
      "cluster_name": "string",
      "description": "string",
      "start_time": "string",
      "end_time": "string"
    }
  ]
}
```

##### POST /exec-logs

**功能描述**：
创建新的执行日志。

**请求参数**：
- from_user_id: 用户ID (必填)
- cluster_name: 集群名称 (必填)
- description: 描述 (可选)
- start_time: 开始时间 (ISO格式，可选)
- end_time: 结束时间 (ISO格式，可选)

**响应示例**：
```json
{
  "ok": true,
  "id": 1
}
```

##### PUT /exec-logs/{log_id}

**功能描述**：
更新指定的执行日志信息。

**请求参数**：
- log_id: 执行日志ID (路径参数，必填)

**请求体**：
```json
{
  "description": "string",
  "start_time": "string",
  "end_time": "string"
}
```

**响应格式**：
```json
{
  "ok": true
}
```

##### DELETE /exec-logs/{log_id}

**功能描述**：
删除指定的执行日志。

**请求参数**：
- log_id: 执行日志ID (路径参数，必填)

**响应格式**：
```json
{
  "ok": true
}
```

### 8. 操作管理 (ops.py)

#### 接口列表

| 方法 | 路径 | 功能描述 | 认证要求 |
|------|------|----------|----------|
| POST | /ops/read-log | 读取远端日志文件内容，支持可选筛选 | 是 |

#### 详细接口说明

##### POST /ops/read-log

**功能描述**：
读取远端日志文件内容，支持可选筛选，仅管理员和操作员可使用。

**请求头**：
```
Authorization: Bearer {token}
```

**请求体**：
```json
{
  "node": "string",
  "path": "string",
  "lines": 200,
  "pattern": "string",
  "sshUser": "string",
  "timeout": 20
}
```

**请求参数说明**：
- node: 目标节点主机名（必填）
- path: 日志文件路径（必填）
- lines: 读取行数，默认为200，范围1-5000（可选）
- pattern: 可选过滤正则（可选）
- sshUser: SSH用户名（可选）
- timeout: 命令超时时间，默认为20秒，范围1-120秒（可选）

**请求示例**：
```json
{
  "node": "hadoop-node1",
  "path": "/var/log/hadoop/hdfs/hadoop-hdfs-datanode.log",
  "lines": 100,
  "pattern": "ERROR",
  "timeout": 30
}
```

**响应格式**：
```json
{
  "execId": "string",
  "exitCode": 0,
  "lines": ["string"]
}
```

**响应示例**：
```json
{
  "execId": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "exitCode": 0,
  "lines": [
    "2025-12-18 00:00:00,000 ERROR [main] org.apache.hadoop.hdfs.server.datanode.DataNode: Initialization failed",
    "2025-12-18 00:00:01,000 ERROR [main] org.apache.hadoop.hdfs.server.datanode.DataNode: java.io.IOException: Failed to bind to port 50010"
  ]
}
```

**错误示例**：
```json
{
  "detail": "not_allowed"
}
```

### 9. AI智能分析 (ai.py)

#### 接口列表

| 方法 | 路径 | 功能描述 | 认证要求 |
|------|------|----------|----------|
| POST | /ai/diagnose-repair | AI诊断与修复 | 是 |
| POST | /ai/chat | AI聊天 | 是 |

#### 详细接口说明

##### POST /ai/diagnose-repair

**功能描述**：
AI诊断与修复，根据提供的条件分析日志并提供修复建议，支持自动修复。

**请求头**：
```
Authorization: Bearer {token}
```

**请求体**：
```json
{
  "cluster": "string",
  "node": "string",
  "timeFrom": "string",
  "keywords": "string",
  "auto": true,
  "maxSteps": 3
}
```

**请求参数说明**：
- cluster: 集群UUID（可选）
- node: 节点主机名（可选）
- timeFrom: ISO起始时间（可选）
- keywords: 关键词（可选）
- auto: 是否允许自动修复，默认为true（可选）
- maxSteps: 最多工具步数，默认为3，范围1-6（可选）

**请求示例**：
```json
{
  "cluster": "123e4567-e89b-12d3-a456-426614174000",
  "node": "hadoop-node1",
  "keywords": "ERROR",
  "auto": true,
  "maxSteps": 3
}
```

**响应格式**：
```json
{
  "result": "string",
  "steps": [
    {
      "action": "string",
      "content": "string",
      "result": "string"
    }
  ],
  "repair": {
    "success": true,
    "details": "string"
  }
}
```

**响应示例**：
```json
{
  "result": "已检测到磁盘空间不足问题",
  "steps": [
    {
      "action": "分析日志",
      "content": "检查hadoop-hdfs-datanode.log",
      "result": "发现磁盘空间不足错误"
    },
    {
      "action": "检查磁盘",
      "content": "df -h",
      "result": "/dev/sda1 已使用95%"
    }
  ],
  "repair": {
    "success": true,
    "details": "已清理临时文件，释放了10GB空间"
  }
}
```

**错误示例**：
```json
{
  "detail": "server_error"
}
```

##### POST /ai/chat

**功能描述**：
AI聊天，与LLM模型进行对话。

**请求头**：
```
Authorization: Bearer {token}
```

**请求体**：
```json
{
  "messages": [
    {
      "role": "string",
      "content": "string"
    }
  ]
}
```

**请求参数说明**：
- messages: 对话消息列表，包含角色和内容（必填）
  - role: 角色，可选值：system, user, assistant
  - content: 消息内容

**请求示例**：
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hadoop NameNode 启动失败怎么办？"
    }
  ]
}
```

**响应格式**：
```json
{
  "reply": "string"
}
```

**响应示例**：
```json
{
  "reply": "Hadoop NameNode 启动失败可能有多种原因，建议检查以下几点：\n1. 检查日志文件 /var/log/hadoop/hdfs/hadoop-hdfs-namenode.log\n2. 验证namenode数据目录权限\n3. 检查fsimage和edits文件是否损坏\n4. 确保端口50070未被占用"
}
```

**错误示例**：
```json
{
  "detail": "llm_unavailable"
}
```

### 10. Hadoop日志管理 (hadoop_logs.py)

#### 接口列表

| 方法 | 路径 | 功能描述 | 认证要求 |
|------|------|----------|----------|
| GET | /logs | 获取Hadoop聚合日志列表 | 是 |
| GET | /hadoop/nodes/ | 获取所有Hadoop节点列表 | 是 |
| GET | /hadoop/logs/{node_name}/{log_type}/ | 获取特定Hadoop节点的日志 | 是 |
| GET | /hadoop/logs/all/{log_type}/ | 获取所有Hadoop节点的日志 | 是 |
| GET | /hadoop/logs/files/{node_name}/ | 获取特定Hadoop节点的日志文件列表 | 是 |
| GET | /hadoop/collectors/status/ | 获取所有Hadoop日志收集器状态 | 是 |
| POST | /hadoop/collectors/start/{node_name}/{log_type}/ | 启动特定Hadoop节点和日志类型的收集 | 是 |
| POST | /hadoop/collectors/stop/{node_name}/{log_type}/ | 停止特定Hadoop节点和日志类型的收集 | 是 |
| POST | /hadoop/collectors/stop/all/ | 停止所有Hadoop日志收集器 | 是 |
| POST | /hadoop/collectors/set-interval/{interval}/ | 设置所有Hadoop收集器的收集间隔 | 是 |
| POST | /hadoop/collectors/set-log-dir/{log_dir}/ | 设置所有Hadoop收集器的日志目录 | 是 |
| POST | /hadoop/nodes/{node_name}/execute/ | 在特定Hadoop节点上执行命令 | 是 |

#### 详细接口说明

##### GET /hadoop/nodes/

**功能描述**：
获取所有Hadoop节点列表。

**请求参数**：
无

**请求头**：
```
Authorization: Bearer {token}
```

**响应格式**：
```json
{
  "nodes": ["string"]
}
```

**响应示例**：
```json
{
  "nodes": ["hadoop-master", "hadoop-node1", "hadoop-node2"]
}
```

##### GET /hadoop/logs/{node_name}/{log_type}/

**功能描述**：
获取特定Hadoop节点的日志。

**请求参数**：
- node_name: 节点名称（路径参数，必填）
- log_type: 日志类型（路径参数，必填）

**请求头**：
```
Authorization: Bearer {token}
```

**响应格式**：
```json
{
  "node_name": "string",
  "log_type": "string",
  "log_content": "string"
}
```

**响应示例**：
```json
{
  "node_name": "hadoop-master",
  "log_type": "namenode",
  "log_content": "2025-12-18 00:00:00,000 INFO NameNode: Starting namenode..."
}
```

##### GET /hadoop/logs/all/{log_type}/

**功能描述**：
获取所有Hadoop节点的日志。

**请求参数**：
- log_type: 日志类型（路径参数，必填）

**请求头**：
```
Authorization: Bearer {token}
```

**响应格式**：
```json
{
  "logs": [
    {
      "node_name": "string",
      "log_type": "string",
      "log_content": "string"
    }
  ]
}
```

**响应示例**：
```json
{
  "logs": [
    {
      "node_name": "hadoop-master",
      "log_type": "namenode",
      "log_content": "2025-12-18 00:00:00,000 INFO NameNode: Starting namenode..."
    },
    {
      "node_name": "hadoop-node1",
      "log_type": "datanode",
      "log_content": "2025-12-18 00:00:01,000 INFO DataNode: Starting datanode..."
    }
  ]
}
```

##### GET /hadoop/logs/files/{node_name}/

**功能描述**：
获取特定Hadoop节点的日志文件列表。

**请求参数**：
- node_name: 节点名称（路径参数，必填）

**请求头**：
```
Authorization: Bearer {token}
```

**响应格式**：
```json
{
  "node_name": "string",
  "log_files": ["string"]
}
```

**响应示例**：
```json
{
  "node_name": "hadoop-master",
  "log_files": ["hadoop-hdfs-namenode.log", "hadoop-hdfs-namenode.out"]
}
```

##### GET /hadoop/collectors/status/

**功能描述**：
获取所有Hadoop日志收集器状态。

**请求参数**：
无

**请求头**：
```
Authorization: Bearer {token}
```

**响应格式**：
```json
{
  "collectors": {
    "string": 0
  },
  "total_running": 0
}
```

**响应示例**：
```json
{
  "collectors": {
    "hadoop-master_namenode": 1,
    "hadoop-node1_datanode": 1
  },
  "total_running": 2
}
```

##### POST /hadoop/collectors/start/{node_name}/{log_type}/

**功能描述**：
启动特定Hadoop节点和日志类型的收集。

**请求参数**：
- node_name: 节点名称（路径参数，必填）
- log_type: 日志类型（路径参数，必填）
- interval: 收集间隔（秒，默认5）

**请求头**：
```
Authorization: Bearer {token}
```

**响应格式**：
```json
{
  "message": "string",
  "interval": 5
}
```

**响应示例**：
```json
{
  "message": "Started log collection for hadoop-master_namenode",
  "interval": 5
}
```

##### POST /hadoop/collectors/stop/{node_name}/{log_type}/

**功能描述**：
停止特定Hadoop节点和日志类型的收集。

**请求参数**：
- node_name: 节点名称（路径参数，必填）
- log_type: 日志类型（路径参数，必填）

**请求头**：
```
Authorization: Bearer {token}
```

**响应格式**：
```json
{
  "message": "string"
}
```

**响应示例**：
```json
{
  "message": "Stopped log collection for hadoop-master_namenode"
}
```

##### POST /hadoop/collectors/stop/all/

**功能描述**：
停止所有Hadoop日志收集器。

**请求参数**：
无

**请求头**：
```
Authorization: Bearer {token}
```

**响应格式**：
```json
{
  "message": "string"
}
```

**响应示例**：
```json
{
  "message": "Stopped all log collectors"
}
```

##### POST /hadoop/collectors/set-interval/{interval}/

**功能描述**：
设置所有Hadoop收集器的收集间隔。

**请求参数**：
- interval: 收集间隔（秒，路径参数，必填）

**请求头**：
```
Authorization: Bearer {token}
```

**响应格式**：
```json
{
  "message": "string"
}
```

**响应示例**：
```json
{
  "message": "Set collection interval to 10 seconds"
}
```

##### POST /hadoop/collectors/set-log-dir/{log_dir}/

**功能描述**：
设置所有Hadoop收集器的日志目录。

**请求参数**：
- log_dir: 日志目录（路径参数，必填）

**请求头**：
```
Authorization: Bearer {token}
```

**响应格式**：
```json
{
  "message": "string"
}
```

**响应示例**：
```json
{
  "message": "Set log directory to /var/log/hadoop"
}
```

##### POST /hadoop/nodes/{node_name}/execute/

**功能描述**：
在特定Hadoop节点上执行命令。

**请求参数**：
- node_name: 节点名称（路径参数，必填）
- command: 要执行的命令（请求体参数，必填）
- timeout: 超时时间（秒，默认30）

**请求头**：
```
Authorization: Bearer {token}
```

**请求体**：
```json
{
  "command": "string",
  "timeout": 30
}
```

**请求示例**：
```json
{
  "command": "hdfs dfsadmin -report",
  "timeout": 60
}
```

**响应格式**：
```json
{
  "node_name": "string",
  "command": "string",
  "stdout": "string",
  "stderr": "string",
  "status": "string"
}
```

**响应示例**：
```json
{
  "node_name": "hadoop-master",
  "command": "hdfs dfsadmin -report",
  "stdout": "Configured Capacity: 1000000000000 (931.32 GB)\nPresent Capacity: 500000000000 (465.66 GB)",
  "stderr": "",
  "status": "success"
}
```

### 11. 用户管理 (users.py)

#### 接口列表

| 方法 | 路径 | 功能描述 | 认证要求 |
|------|------|----------|----------|
| GET | /users | 获取所有用户列表（仅管理员） | 是 |
| POST | /users | 创建新用户（仅管理员） | 是 |
| PATCH | /users/{username} | 更新用户信息（仅管理员） | 是 |
| DELETE | /users/{username} | 删除用户（仅管理员） | 是 |

#### 详细接口说明

##### GET /users

**功能描述**：
获取所有用户列表，仅管理员可访问。

**请求参数**：
无

**请求头**：
```
Authorization: Bearer {token}
```

**响应格式**：
```json
{
  "users": [
    {
      "username": "string",
      "email": "string",
      "role": "string",
      "status": "string"
    }
  ]
}
```

**响应示例**：
```json
{
  "users": [
    {
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin",
      "status": "enabled"
    },
    {
      "username": "ops",
      "email": "ops@example.com",
      "role": "operator",
      "status": "enabled"
    }
  ]
}
```

**错误示例**：
```json
{
  "detail": "not_admin"
}
```

##### POST /users

**功能描述**：
创建新用户，仅管理员可访问。

**请求头**：
```
Authorization: Bearer {token}
```

**请求体**：
```json
{
  "username": "string",
  "email": "string",
  "role": "string",
  "status": "string"
}
```

**请求参数说明**：
- username: 用户名，3-50个字符，以字母开头，支持字母/数字/下划线（必填）
- email: 电子邮箱（必填）
- role: 角色，可选值：admin, operator, observer（必填）
- status: 状态，可选值：enabled, pending, disabled（必填）

**请求示例**：
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "role": "observer",
  "status": "enabled"
}
```

**响应格式**：
```json
{
  "ok": true
}
```

**错误示例**：
```json
{
  "detail": {
    "errors": [
      {
        "field": "username",
        "message": "用户名已存在"
      }
    ]
  }
}
```

##### PATCH /users/{username}

**功能描述**：
更新用户信息，仅管理员可访问。

**请求参数**：
- username: 用户名（路径参数，必填）

**请求头**：
```
Authorization: Bearer {token}
```

**请求体**：
```json
{
  "role": "string",
  "status": "string"
}
```

**请求参数说明**：
- role: 角色，可选值：admin, operator, observer（可选）
- status: 状态，可选值：enabled, disabled（可选）

**请求示例**：
```json
{
  "role": "operator",
  "status": "enabled"
}
```

**响应格式**：
```json
{
  "ok": true
}
```

**错误示例**：
```json
{
  "detail": "not_found"
}
```

##### DELETE /users/{username}

**功能描述**：
删除用户，仅管理员可访问。

**请求参数**：
- username: 用户名（路径参数，必填）

**请求头**：
```
Authorization: Bearer {token}
```

**响应格式**：
```json
{
  "ok": true
}
```

**错误示例**：
```json
{
  "detail": "not_admin"
}
```

### 12. 安全相关 (secure.py)

**说明**：安全相关模块当前只包含一个获取当前用户信息的接口，该接口已在身份认证模块中详细描述。

### 13. 系统操作日志 (sys_exec_logs.py)

#### 接口列表

| 方法 | 路径 | 功能描述 | 认证要求 |
|------|------|----------|----------|
| GET | /sys-exec-logs | 获取系统操作日志列表 | 是 |
| POST | /sys-exec-logs | 创建系统操作日志 | 是 |
| DELETE | /sys-exec-logs/{operation_id} | 删除系统操作日志 | 是 |

#### 详细接口说明

##### GET /sys-exec-logs

**功能描述**：
获取系统操作日志列表，支持分页。

**请求参数**：
- page: 页码 (默认1)
- size: 每页数量 (默认10)

**响应格式**：
```json
{
  "items": [
    {
      "operation_id": "string",
      "user_id": 0,
      "description": "string",
      "operation_time": "string"
    }
  ],
  "total": 0
}
```

##### POST /sys-exec-logs

**功能描述**：
创建系统操作日志。

**请求参数**：
- user_id: 用户ID (必填)
- description: 操作描述 (必填)

**响应示例**：
```json
{
  "ok": true,
  "operation_id": "uuid-string"
}
```

## 数据模型

### 用户模型 (User)

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | int | 用户ID |
| username | str | 用户名，最大50字符，唯一 |
| email | str | 电子邮箱，最大100字符，唯一 |
| password_hash | str | 密码哈希，最大255字符 |
| full_name | str | 全名，最大100字符 |
| is_active | bool | 是否激活，默认True |
| last_login | datetime | 最后登录时间 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 集群模型 (Cluster)

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | int | 集群ID |
| uuid | UUID | 集群UUID，唯一 |
| name | str | 集群名称，最大100字符，唯一 |
| type | str | 集群类型，最大50字符 |
| node_count | int | 节点数量，默认0 |
| health_status | str | 健康状态，默认"unknown"，最大20字符 |
| description | str | 集群描述 |
| config_info | JSON | 配置信息 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 节点模型 (Node)

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | int | 节点ID |
| uuid | UUID | 节点UUID，唯一 |
| cluster_id | int | 所属集群ID |
| hostname | str | 主机名，最大100字符 |
| ip_address | INET | IP地址 |
| status | str | 节点状态，默认"unknown"，最大20字符 |
| cpu_usage | float | CPU使用率 |
| memory_usage | float | 内存使用率 |
| disk_usage | float | 磁盘使用率 |
| last_heartbeat | datetime | 最后心跳时间 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### Hadoop日志模型 (HadoopLog)

| 字段名 | 类型 | 描述 |
|--------|------|------|
| log_id | int | 日志ID (主键, 自增) |
| cluster_name | str | 集群名称 |
| node_host | str | 节点主机名 |
| title | str | 日志标题 |
| info | str | 日志详细信息 |
| log_time | datetime | 日志时间 |

### Hadoop执行日志模型 (HadoopExecLog)

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | int | 执行日志ID (主键, 自增) |
| from_user_id | int | 操作用户ID |
| cluster_name | str | 集群名称 |
| description | str | 执行描述 |
| start_time | datetime | 开始时间 |
| end_time | datetime | 结束时间 |

### 系统操作日志模型 (SysExecLog)

| 字段名 | 类型 | 描述 |
|--------|------|------|
| operation_id | UUID | 操作ID (主键, UUID) |
| user_id | int | 用户ID |
| description | str | 操作描述 |
| operation_time | datetime | 操作时间 |

## 认证与授权

### 认证方式

- **JWT Token**: 使用JSON Web Token进行认证
- **登录接口**: `/api/v1/login` 获取访问令牌和刷新令牌
- **刷新令牌**: `/api/v1/refresh` 用于刷新访问令牌
- **登出接口**: `/api/v1/logout` 使令牌失效

### 授权角色

- **admin**: 管理员，拥有所有权限
- **operator**: 操作员，拥有操作权限
- **observer**: 查看员，只有查看权限

## 错误处理

### 错误响应格式

```json
{
  "detail": "错误描述"
}
```

### 常见错误码

| 状态码 | 描述 |
|--------|------|
| 400 | 请求错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

## 开发与部署

### 开发环境

```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python -m uvicorn app.main:app --reload
```

### 生产环境

```bash
# 安装依赖
pip install -r requirements.txt

# 启动生产服务器
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 监控与维护

### 日志

- 应用日志：由FastAPI内置日志系统记录
- Hadoop日志：通过`hadoop_logs`模块收集和分析
- 执行日志：通过`exec_logs`模块记录操作执行情况

### 指标

- 系统指标：CPU、内存、磁盘使用情况
- 服务指标：请求数、响应时间、错误率
- Hadoop指标：集群状态、节点状态、作业状态

## 版本历史

| 版本 | 日期 | 描述 |
|------|------|------|
| v1 | 2025-12-16 | 初始版本 |

## 联系方式

- 开发团队：Hadoop故障检测团队
- 邮箱：support@hadoop-fault-detect.example.com
- 文档：http://localhost:8000/docs
- 红文档：http://localhost:8000/redoc

## 许可证

MIT License
