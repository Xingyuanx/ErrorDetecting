# FastAPI Hadoop日志读取系统部署手册

## 1. 项目概述

本项目是一个基于FastAPI的Hadoop集群日志远程读取系统，允许用户通过API接口远程访问和管理Hadoop集群的日志文件。

### 主要功能
- 获取Hadoop集群节点列表
- 读取指定节点的日志文件
- 读取所有节点的日志文件
- 将日志保存到本地
- 实时日志收集
- 远程执行命令

## 2. 环境准备

### 2.1 系统要求
- Python 3.8+ 
- 任意支持Python开发的IDE（PyCharm、VS Code、Eclipse等）
- 网络连接正常，能访问目标Hadoop集群

### 2.2 依赖安装

项目依赖已在`requirements.txt`文件中定义，安装命令：

```bash
pip install -r requirements.txt
```

主要依赖包：
- fastapi: Web框架
- uvicorn: ASGI服务器
- paramiko: SSH连接工具
- python-dotenv: 环境变量管理
- pydantic-settings: 配置管理

## 3. 部署步骤

### 3.1 代码获取

将项目代码复制到本地IDE工作目录，确保包含以下文件和目录：
- `app/`：核心应用代码
- `config.py`：配置文件
- `requirements.txt`：依赖列表
- `.env`：环境变量配置

### 3.2 配置文件修改

根据目标Hadoop集群的实际情况，修改以下配置文件：

#### 3.2.1 `.env` 文件

`.env`文件包含了Hadoop集群的核心配置，需要根据实际集群情况修改：

```env
# Hadoop Cluster Configuration
HADOOP_HOME=/opt/module/hadoop-3.1.3  # 修改为目标集群的Hadoop安装目录
LOG_DIR=/opt/module/hadoop-3.1.3/logs  # 修改为目标集群的日志目录

# Hadoop Nodes Configuration
# Format: NODE_NAME=ip,username,password
NODE_HADOOP102=192.168.10.102,hadoop,your_password  # 修改为实际节点信息
NODE_HADOOP103=192.168.10.103,hadoop,your_password  # 修改为实际节点信息
NODE_HADOOP104=192.168.10.104,hadoop,your_password  # 修改为实际节点信息
NODE_HADOOP105=192.168.10.105,hadoop,your_password  # 修改为实际节点信息
NODE_HADOOP100=192.168.10.100,hadoop,your_password  # 修改为实际节点信息

# SSH Configuration
SSH_PORT=22  # 修改为实际SSH端口
SSH_TIMEOUT=10  # SSH连接超时时间
```

#### 3.2.2 节点服务配置

在`app/main.py`文件中，需要根据目标集群的实际服务部署情况修改节点服务配置：

```python
# Node service configuration based on cluster setup
# Format: node_name: [service1, service2, ...]
node_services = {
    "hadoop102": ["namenode", "datanode", "nodemanager"],  # 修改为实际服务
    "hadoop103": ["datanode", "resourcemanager", "nodemanager"],  # 修改为实际服务
    "hadoop104": ["datanode", "secondarynamenode", "nodemanager"],  # 修改为实际服务
    "hadoop105": ["datanode", "nodemanager"],  # 修改为实际服务
    "hadoop100": ["datanode", "nodemanager"]  # 修改为实际服务
}
```

### 3.3 项目启动

#### 3.3.1 开发模式启动

在IDE中运行`app/main.py`文件，或使用以下命令启动：

```bash
uvicorn app.main:app --reload
```

#### 3.3.2 生产模式启动

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3.4 验证部署

启动成功后，访问以下地址验证服务：
- API文档：`http://localhost:8000/docs`
- 根路径：`http://localhost:8000/`

## 4. Hadoop集群差异处理

当目标Hadoop集群与原开发环境不同时，需要重点修改以下几个方面：

### 4.1 节点配置

1. **节点数量和名称**：
   - 修改`.env`文件中`NODE_*`环境变量，添加或删除节点配置
   - 确保节点名称与实际Hadoop集群节点名称一致

2. **节点IP和认证信息**：
   - 修改每个节点的IP地址、用户名和密码
   - 确保SSH连接信息正确

### 4.2 服务部署差异

1. **服务类型和分布**：
   - 修改`app/main.py`中的`node_services`字典
   - 根据实际集群中每个节点运行的服务进行配置
   - 常见服务包括：namenode、datanode、resourcemanager、nodemanager、secondarynamenode等

2. **服务日志文件命名**：
   - 检查`app/log_reader.py`中的日志文件命名规则
   - 确保与目标集群的日志文件命名一致

### 4.3 路径配置

1. **Hadoop安装路径**：
   - 修改`.env`文件中的`HADOOP_HOME`变量
   - 确保与目标集群的Hadoop安装路径一致

2. **日志目录路径**：
   - 修改`.env`文件中的`LOG_DIR`变量
   - 确保与目标集群的日志存储路径一致

3. **日志文件位置**：
   - 检查`app/log_reader.py`中的日志文件路径构建逻辑
   - 确保能正确定位到目标集群的日志文件

### 4.4 SSH配置

1. **SSH端口**：
   - 修改`.env`文件中的`SSH_PORT`变量
   - 确保与目标集群的SSH服务端口一致

2. **SSH超时时间**：
   - 根据网络环境调整`.env`文件中的`SSH_TIMEOUT`变量
   - 确保能在超时时间内建立SSH连接

## 5. 核心代码结构说明

### 5.1 主要模块

| 模块名 | 功能描述 | 文件位置 |
|--------|----------|----------|
| main | 应用入口，定义API路由 | app/main.py |
| log_reader | 日志读取和管理 | app/log_reader.py |
| log_collector | 实时日志收集 | app/log_collector.py |
| ssh_utils | SSH连接管理 | app/ssh_utils.py |
| schemas | 数据模型定义 | app/schemas.py |
| config | 配置管理 | config.py |

### 5.2 关键配置文件

| 文件名 | 功能描述 | 重点修改项 |
|--------|----------|------------|
| .env | 环境变量配置 | 节点信息、路径配置、SSH配置 |
| config.py | 配置类定义 | 配置逻辑（如需扩展） |
| app/main.py | 服务启动配置 | 节点服务映射 |

## 6. 常见问题排查

### 6.1 SSH连接失败

**症状**：无法连接到Hadoop节点

**排查步骤**：
1. 检查`.env`文件中节点IP、用户名、密码是否正确
2. 验证目标节点SSH服务是否正常运行
3. 检查网络连接是否正常，防火墙是否允许SSH连接
4. 查看应用日志，确认具体错误信息

### 6.2 日志文件找不到

**症状**：API返回日志文件不存在错误

**排查步骤**：
1. 检查`LOG_DIR`配置是否正确
2. 验证目标节点上实际日志文件路径和命名
3. 检查`app/log_reader.py`中的日志文件命名规则
4. 确保用户有读取日志文件的权限

### 6.3 服务启动失败

**症状**：应用无法启动

**排查步骤**：
1. 检查Python版本是否符合要求
2. 验证依赖包是否正确安装
3. 查看启动日志，确认具体错误信息
4. 检查配置文件格式是否正确

## 7. API使用说明

### 7.1 节点管理

- 获取节点列表：`GET /api/nodes/`
- 在节点上执行命令：`POST /api/nodes/{node_name}/execute/`

### 7.2 日志管理

- 获取指定节点日志：`GET /api/logs/{node_name}/{log_type}/`
- 获取所有节点日志：`GET /api/logs/all/{log_type}/`
- 保存日志到本地：`POST /api/logs/save/`
- 获取日志文件列表：`GET /api/logs/files/{node_name}/`

### 7.3 日志收集管理

- 获取收集器状态：`GET /api/collectors/status/`
- 启动日志收集：`POST /api/collectors/start/{node_name}/{log_type}/`
- 停止日志收集：`POST /api/collectors/stop/{node_name}/{log_type}/`
- 停止所有收集器：`POST /api/collectors/stop/all/`
- 设置收集间隔：`POST /api/collectors/set-interval/{interval}/`
- 设置日志目录：`POST /api/collectors/set-log-dir/{log_dir}/`

## 8. 扩展和定制

### 8.1 添加新的日志类型

1. 在`app/log_reader.py`中扩展日志文件映射逻辑
2. 确保`node_services`配置中包含新的日志类型

### 8.2 修改日志收集逻辑

1. 编辑`app/log_collector.py`文件
2. 调整日志收集间隔、保存策略等

### 8.3 添加新的API端点

1. 在`app/main.py`中添加新的路由
2. 在`app/schemas.py`中定义数据模型
3. 实现相应的业务逻辑

## 9. 安全注意事项

1. **密码管理**：
   - 生产环境中建议使用SSH密钥认证替代密码认证
   - 避免在代码中硬编码密码

2. **访问控制**：
   - 生产环境中建议添加API认证机制
   - 限制API访问IP范围

3. **日志安全**：
   - 确保日志中不包含敏感信息
   - 定期清理日志文件

4. **权限管理**：
   - 确保运行应用的用户权限适当
   - 避免使用root用户运行应用

## 10. 监控和维护

1. **应用日志**：
   - 定期查看应用日志，及时发现问题
   - 可配置日志轮转策略

2. **性能监控**：
   - 监控API响应时间和资源使用情况
   - 可使用Prometheus、Grafana等工具进行监控

3. **定期更新**：
   - 定期更新依赖包，修复安全漏洞
   - 关注Hadoop和相关组件的更新

---

本部署手册涵盖了在其他IDE环境中部署该Hadoop日志读取系统的主要步骤和注意事项。根据实际环境的不同，可能需要进行额外的调整和配置。