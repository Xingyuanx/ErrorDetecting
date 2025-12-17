# Hadoop Fault Detecting API 部署手册

## 1. 项目概述

Hadoop Fault Detecting API是一个基于FastAPI开发的后端服务，用于监控和管理Hadoop集群，提供集群管理、节点监控、日志分析、故障检测等功能。

## 2. 环境要求

### 2.1 硬件要求

| 配置项 | 最低要求 | 推荐配置 |
|--------|----------|----------|
| CPU | 4核 | 8核 |
| 内存 | 8GB | 16GB |
| 磁盘 | 100GB | 200GB |
| 网络 | 千兆网卡 | 万兆网卡 |

### 2.2 软件要求

| 软件 | 版本 | 说明 |
|------|------|------|
| Python | 3.13+ | 开发和运行环境 |
| PostgreSQL | 14+ | 数据库 |
| Redis | 6.0+ | 可选，用于缓存 |
| Git | 2.0+ | 版本控制 |
| Nginx | 1.18+ | 反向代理（可选） |
| Docker | 20.10+ | 容器化部署（可选） |
| Docker Compose | 1.29+ | 容器编排（可选） |

## 3. 部署准备

### 3.1 克隆代码

```bash
# 克隆代码到本地
git clone https://github.com/your-repo/hadoop-fault-detecting.git
cd hadoop-fault-detecting
```

### 3.2 安装Python依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3.3 配置环境变量

创建`.env`文件，配置以下环境变量：

```env
# 数据库配置
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/hadoop_fault

# JWT配置
JWT_SECRET=your_jwt_secret_key
JWT_EXPIRE_MINUTES=30

# LLM配置
OPENAI_API_KEY=your_openai_api_key

# Hadoop节点配置
HADOOP_NODES={"hadoop-master": "192.168.1.100", "hadoop-node1": "192.168.1.101"}

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=app.log
```

## 4. 数据库部署

### 4.1 安装PostgreSQL

#### Ubuntu

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib -y

# 启动PostgreSQL服务
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### CentOS

```bash
sudo dnf install postgresql-server postgresql-contrib -y

# 初始化数据库
sudo postgresql-setup initdb

# 启动PostgreSQL服务
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Windows

下载安装包：https://www.postgresql.org/download/windows/

按照安装向导进行安装，记住设置的密码。

### 4.2 创建数据库和用户

```bash
# 登录PostgreSQL
sudo -u postgres psql

# 创建数据库
CREATE DATABASE hadoop_fault;

# 创建用户
CREATE USER username WITH PASSWORD 'password';

# 授权用户访问数据库
GRANT ALL PRIVILEGES ON DATABASE hadoop_fault TO username;

# 退出PostgreSQL\q
```

### 4.3 初始化数据库

```bash
# 运行数据库迁移（如果有）
# alembic upgrade head

# 或直接启动服务，FastAPI会自动创建表
python -m uvicorn app.main:app --reload
```

## 5. 服务部署

### 5.1 直接部署

#### 开发环境

```bash
# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 启动开发服务器
python -m uvicorn app.main:app --reload
```

访问地址：
- API文档：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

#### 生产环境

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动生产服务器
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5.2 使用systemd部署

创建systemd服务文件：`/etc/systemd/system/hadoop-fault-api.service`

```ini
[Unit]
Description=Hadoop Fault Detecting API
After=network.target postgresql.service

[Service]
User=your_user
Group=your_group
WorkingDirectory=/path/to/hadoop-fault-detecting
Environment="PATH=/path/to/hadoop-fault-detecting/venv/bin"
ExecStart=/path/to/hadoop-fault-detecting/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start hadoop-fault-api
sudo systemctl enable hadoop-fault-api
```

查看服务状态：

```bash
sudo systemctl status hadoop-fault-api
sudo journalctl -u hadoop-fault-api -f
```

### 5.3 使用Docker部署

#### 构建Docker镜像

创建`Dockerfile`：

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动服务
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

创建`.dockerignore`文件：

```
__pycache__
venv
.env
*.log
.git
```

构建镜像：

```bash
docker build -t hadoop-fault-api .
```

#### 使用Docker Compose

创建`docker-compose.yml`文件：

```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: hadoop_fault
      POSTGRES_USER: username
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  api:
    build: .
    environment:
      DATABASE_URL: postgresql+asyncpg://username:password@db:5432/hadoop_fault
      JWT_SECRET: your_jwt_secret_key
      JWT_EXPIRE_MINUTES: 30
      OPENAI_API_KEY: your_openai_api_key
    ports:
      - "8000:8000"
    depends_on:
      - db
    restart: unless-stopped

volumes:
  postgres_data:
```

启动服务：

```bash
docker-compose up -d
```

查看日志：

```bash
docker-compose logs -f
```

停止服务：

```bash
docker-compose down
```

## 6. 配置说明

### 6.1 主要配置文件

| 配置文件 | 作用 | 位置 |
|----------|------|------|
| .env | 环境变量配置 | 项目根目录 |
| app/config.py | 应用配置 | app/ |
| requirements.txt | Python依赖 | 项目根目录 |

### 6.2 环境变量说明

| 环境变量 | 类型 | 说明 | 示例 |
|----------|------|------|------|
| DATABASE_URL | 字符串 | 数据库连接URL | postgresql+asyncpg://username:password@localhost:5432/hadoop_fault |
| JWT_SECRET | 字符串 | JWT密钥 | your_jwt_secret_key |
| JWT_EXPIRE_MINUTES | 整数 | JWT令牌有效期（分钟） | 30 |
| OPENAI_API_KEY | 字符串 | OpenAI API密钥 | sk-xxxxxxxxxxxxxxxxxx |
| HADOOP_NODES | JSON字符串 | Hadoop节点配置 | {"hadoop-master": "192.168.1.100"} |
| LOG_LEVEL | 字符串 | 日志级别 | INFO |
| LOG_FILE | 字符串 | 日志文件路径 | app.log |

### 6.3 应用配置说明

在`app/config.py`中可以配置应用的各种参数：

```python
# 应用配置
APP_TITLE = "Hadoop Fault Detecting API"
APP_VERSION = "v1"

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL")

# JWT配置
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 30))

# LLM配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Hadoop节点配置
HADOOP_NODES = json.loads(os.getenv("HADOOP_NODES", "{}"))

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "app.log")
```

## 7. 反向代理配置

### 7.1 使用Nginx

创建Nginx配置文件：`/etc/nginx/conf.d/hadoop-fault-api.conf`

```nginx
server {
    listen 80;
    server_name api.example.com;

    # 日志配置
    access_log /var/log/nginx/hadoop-fault-api.access.log;
    error_log /var/log/nginx/hadoop-fault-api.error.log;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件配置（如果有）
    location /static/ {
        alias /path/to/hadoop-fault-detecting/static/;
        expires 30d;
    }
}
```

测试并重启Nginx：

```bash
sudo nginx -t
sudo systemctl restart nginx
```

### 7.2 使用HTTPS

生成SSL证书：

```bash
sudo certbot certonly --nginx -d api.example.com
```

更新Nginx配置：

```nginx
server {
    listen 80;
    server_name api.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name api.example.com;

    # SSL证书配置
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # 其他配置...
    location / {
        proxy_pass http://localhost:8000;
        # 其他proxy配置...
    }
}
```

## 8. 监控和维护

### 8.1 日志监控

应用日志默认保存在项目根目录的`app.log`文件中，可以通过以下命令查看日志：

```bash
# 实时查看日志
tail -f app.log

# 查看错误日志
grep -i error app.log

# 查看特定时间段的日志
grep "2025-12-18" app.log
```

### 8.2 健康检查

应用提供了健康检查接口，可以通过以下命令检查服务状态：

```bash
curl http://localhost:8000/api/v1/health
```

响应示例：

```json
{
  "status": "ok",
  "database": "connected"
}
```

### 8.3 数据库备份

定期备份数据库：

```bash
# 备份数据库
pg_dump -U username -d hadoop_fault > hadoop_fault_backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复数据库
psql -U username -d hadoop_fault < hadoop_fault_backup.sql
```

### 8.4 性能监控

可以使用以下工具监控服务性能：

- **Prometheus + Grafana**：监控系统和应用性能
- **New Relic**：应用性能监控
- **ELK Stack**：日志收集和分析

## 9. 常见问题和解决方案

### 9.1 数据库连接失败

**问题**：启动服务时提示数据库连接失败

**解决方案**：
1. 检查数据库服务是否正在运行
2. 检查数据库连接URL是否正确
3. 检查数据库用户权限是否正确
4. 检查防火墙设置是否允许连接

### 9.2 端口被占用

**问题**：启动服务时提示端口8000已被占用

**解决方案**：
1. 查找占用端口的进程：`lsof -i :8000`
2. 终止占用端口的进程：`kill -9 <PID>`
3. 或修改服务端口：`uvicorn app.main:app --port 8001`

### 9.3 依赖安装失败

**问题**：安装依赖时出现错误

**解决方案**：
1. 确保Python版本符合要求
2. 更新pip：`pip install --upgrade pip`
3. 安装系统依赖：
   - Ubuntu：`apt install build-essential libpq-dev`
   - CentOS：`yum install gcc gcc-c++ postgresql-devel`
4. 尝试使用国内镜像源：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt`

### 9.4 JWT令牌无效

**问题**：请求API时提示"Invalid credentials"

**解决方案**：
1. 检查JWT_SECRET是否正确配置
2. 检查令牌是否过期
3. 检查令牌格式是否正确
4. 检查请求头中是否正确携带令牌

### 9.5 500服务器错误

**问题**：请求API时返回500错误

**解决方案**：
1. 查看应用日志，定位错误原因
2. 检查数据库连接是否正常
3. 检查代码中是否有未处理的异常
4. 检查依赖版本是否兼容

## 10. 更新和升级

### 10.1 代码更新

```bash
# 拉取最新代码
git pull

# 安装新依赖
pip install -r requirements.txt

# 重启服务
# 直接部署：重启uvicorn服务
# systemd部署：sudo systemctl restart hadoop-fault-api
# Docker部署：docker-compose up -d --build
```

### 10.2 数据库迁移

如果使用Alembic进行数据库迁移：

```bash
# 创建迁移脚本
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head
```

## 11. 安全最佳实践

1. **使用HTTPS**：生产环境中使用HTTPS加密传输
2. **定期更新依赖**：定期更新Python依赖，修复安全漏洞
3. **限制访问权限**：设置适当的文件和目录权限
4. **配置防火墙**：限制只有特定IP可以访问服务
5. **使用强密码**：数据库和用户密码使用强密码
6. **定期备份**：定期备份数据库和配置文件
7. **监控日志**：实时监控日志，及时发现异常
8. **使用VPN**：如果服务部署在公网，考虑使用VPN访问

## 12. 联系方式

- **开发团队**：Hadoop故障检测团队
- **文档地址**：`docs/deployment_guide.md`
- **版本历史**：
  - v1.0 (2025-12-18)：初始版本

---

**注意**：本部署手册将根据项目的更新不断完善，建议定期查看最新版本。