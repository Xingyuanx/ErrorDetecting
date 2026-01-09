# Enterprise Cluster Management Console | 企业级集群管理控制台

![Vue.js](https://img.shields.io/badge/vue-%2335495e.svg?style=flat&logo=vuedotjs&logoColor=%234FC08D)
![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=flat&logo=typescript&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Python](https://img.shields.io/badge/python-3670A0?style=flat&logo=python&logoColor=ffdd54)
![PostgreSQL](https://img.shields.io/badge/postgresql-4169e1?style=flat&logo=postgresql&logoColor=white)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

---

## 📖 目录 / Table of Contents

- [中文介绍 (Chinese Version)](#-中文介绍-chinese-version)
  - [项目简介](#-项目简介)
  - [核心技术栈](#-核心技术栈)
  - [功能特性](#-功能特性)
  - [快速开始](#-快速开始)
  - [目录结构](#-目录结构)
  - [贡献指南](#-贡献指南)
  - [许可证](#-许可证)
- [English Description](#-english-description)
  - [Overview](#-overview)
  - [Tech Stack](#-tech-stack)
  - [Features](#-features)
  - [Quick Start](#-quick-start)
  - [Directory Structure](#-directory-structure)
  - [Contributing](#-contributing)
  - [License](#-license)

---

## 🇨🇳 中文介绍 (Chinese Version)

### 🚀 项目简介

**企业级集群管理控制台** 是一款集监控、诊断、运维于一体的现代化大数据平台管理工具。项目采用前后端分离架构，前端基于 Vue 3 + TypeScript 构建高性能交互界面，后端基于 FastAPI + Python 提供高效的异步处理能力和 AI 智能诊断服务。

### 🛠 核心技术栈

#### 前端 (Frontend)

- **框架**: Vue.js 3 (Composition API)
- **语言**: TypeScript
- **构建工具**: Vite
- **UI 组件库**: Element Plus
- **状态管理**: Pinia
- **图表库**: ECharts
- **测试**: Vitest + Playwright

#### 后端 (Backend)

- **框架**: FastAPI (Python 异步 Web 框架)
- **数据库**: PostgreSQL (Asyncpg 驱动)
- **ORM**: SQLAlchemy (Async)
- **AI/LLM**: LangChain + OpenAI (智能诊断)
- **运维工具**: Paramiko (SSH), PyJWT (认证)

### ✨ 功能特性

1.  **可视化监控 (Dashboard)**
    - 实时展示集群节点状态（健康/警告/宕机）。
    - 动态渲染 CPU 和内存利用率趋势图表。
2.  **智能诊断 (Intelligent Diagnosis)**
    - 基于 LLM 的自动化诊断工具，一键检测 Hadoop/Spark 组件异常。
    - 提供详细的根因分析报告和修复建议。
3.  **全链路日志分析 (Log Analysis)**
    - 支持系统日志、执行日志和操作日志的多维度检索。
    - 提供高亮显示和日志下载功能。
4.  **企业级安全 (Enterprise Security)**
    - 完善的 RBAC（基于角色的访问控制）权限体系。
    - 基于 JWT 的双 Token 认证机制（Access + Refresh）。

### ⚡ 快速开始 (Quick Start)

**前置要求：**

- Node.js >= 18.0.0
- Python >= 3.10
- PostgreSQL >= 14
- pnpm (推荐)

#### 1. 克隆项目

```bash
git clone <repository-url>
cd project
```

#### 2. 启动后端服务

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端 API 文档地址: `http://localhost:8000/docs`

#### 3. 启动前端服务

```bash
cd ../frontend-vue

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev
```

访问 `http://localhost:5173` 即可预览项目。

### 📂 目录结构

```text
/home/devbox/project/
├── frontend-vue/             # 前端项目 (Vue 3 + TS)
│   ├── src/
│   │   ├── api/              # API 接口服务
│   │   ├── views/            # 页面视图
│   │   └── ...
│   └── ...
├── backend/                  # 后端项目 (FastAPI + Python)
│   ├── app/
│   │   ├── routers/          # API 路由
│   │   ├── services/         # 业务逻辑 (AI 诊断, SSH)
│   │   ├── models/           # 数据库模型
│   │   └── main.py           # 入口文件
│   └── requirements.txt      # Python 依赖
└── README.md                 # 项目说明文档
```

### 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库。
2. 创建一个新的分支 (`git checkout -b feature/AmazingFeature`)。
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)。
4. 推送到分支 (`git push origin feature/AmazingFeature`)。
5. 开启一个 Pull Request。

### 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

---

## 🇺🇸 English Description

### 🚀 Overview

**Enterprise Cluster Management Console** is a modern big data platform management tool integrating monitoring, diagnosis, and operations. Built with a separated frontend-backend architecture, it features a high-performance UI powered by Vue 3 + TypeScript and an efficient asynchronous backend powered by FastAPI + Python, providing AI-driven intelligent diagnosis services.

### 🛠 Tech Stack

#### Frontend

- **Framework**: Vue.js 3 (Composition API)
- **Language**: TypeScript
- **Build Tool**: Vite
- **UI Library**: Element Plus
- **State Management**: Pinia
- **Charting**: ECharts
- **Testing**: Vitest + Playwright

#### Backend

- **Framework**: FastAPI (Python Async Web Framework)
- **Database**: PostgreSQL (Asyncpg driver)
- **ORM**: SQLAlchemy (Async)
- **AI/LLM**: LangChain + OpenAI (Intelligent Diagnosis)
- **Ops Tools**: Paramiko (SSH), PyJWT (Auth)

### ✨ Features

1.  **Visual Monitoring (Dashboard)**
    - Real-time display of cluster node status (Health/Warning/Down).
    - Dynamic rendering of CPU and Memory usage trends.
2.  **Intelligent Diagnosis**
    - LLM-based automated diagnostic tools to detect Hadoop/Spark component anomalies.
    - Provides detailed root cause analysis and repair suggestions.
3.  **Full-Link Log Analysis**
    - Multi-dimensional search for system logs, execution logs, and operation logs.
    - Syntax highlighting and log download capabilities.
4.  **Enterprise Security**
    - Comprehensive RBAC (Role-Based Access Control) system.
    - JWT-based dual token authentication mechanism (Access + Refresh).

### ⚡ Quick Start

**Prerequisites:**

- Node.js >= 18.0.0
- Python >= 3.10
- PostgreSQL >= 14
- pnpm (recommended)

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd project
```

#### 2. Start Backend Service

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API Docs: `http://localhost:8000/docs`

#### 3. Start Frontend Service

```bash
cd ../frontend-vue

# Install dependencies
pnpm install

# Start dev server
pnpm dev
```

Access `http://localhost:5173` to preview.

### 📂 Directory Structure

```text
/home/devbox/project/
├── frontend-vue/             # Frontend Project (Vue 3 + TS)
│   ├── src/
│   │   ├── api/              # API Services
│   │   ├── views/            # Page Views
│   │   └── ...
│   └── ...
├── backend/                  # Backend Project (FastAPI + Python)
│   ├── app/
│   │   ├── routers/          # API Routers
│   │   ├── services/         # Business Logic (AI, SSH)
│   │   ├── models/           # DB Models
│   │   └── main.py           # Entry Point
│   └── requirements.txt      # Python Dependencies
└── README.md                 # Documentation
```

### 🤝 Contributing

Contributions are welcome!

1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

### 📄 License

This project is licensed under the [MIT License](LICENSE).
