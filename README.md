# Enterprise Cluster Management Console | 企业级集群管理控制台

![Vue.js](https://img.shields.io/badge/vue-%2335495e.svg?style=flat&logo=vuedotjs&logoColor=%234FC08D)
![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=flat&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=flat&logo=vite&logoColor=white)
![Element Plus](https://img.shields.io/badge/Element%20Plus-409EFF?style=flat&logo=element-plus&logoColor=white)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

---

## 📖 目录 / Table of Contents

- [中文介绍 (Chinese Version)](#-中文介绍-chinese-version)
  - [项目简介](#-项目简介)
  - [功能特性](#-功能特性)
  - [安装指南](#-安装指南)
  - [使用说明](#-使用说明)
  - [目录结构](#-目录结构)
  - [贡献指南](#-贡献指南)
  - [许可证](#-许可证)
- [English Description](#-english-description)
  - [Overview](#-overview)
  - [Features](#-features)
  - [Installation](#-installation)
  - [Usage](#-usage)
  - [Directory Structure](#-directory-structure)
  - [Contributing](#-contributing)
  - [License](#-license)

---

## 🇨🇳 中文介绍 (Chinese Version)

### 🚀 项目简介
**企业级集群管理控制台** 是一个基于现代化前端技术栈（Vue 3 + TypeScript + Vite）构建的高性能 Web 应用。该项目专为大数据运维团队设计，提供了一站式的集群监控、日志分析和故障诊断解决方案。通过直观的可视化界面，帮助用户实时掌握集群健康状态，快速定位并解决系统异常。

**核心技术栈：**
- **框架**: Vue.js 3 (Composition API)
- **语言**: TypeScript
- **构建工具**: Vite
- **UI 组件库**: Element Plus
- **状态管理**: Pinia
- **图表库**: ECharts
- **测试**: Vitest (单元测试) + Playwright (E2E)

### ✨ 功能特性
1.  **可视化监控 (Dashboard)**
    - 实时展示集群节点状态（健康/警告/宕机）。
    - 动态渲染 CPU 和内存利用率趋势图表。
2.  **智能诊断 (Intelligent Diagnosis)**
    - 内置自动化诊断工具，一键检测 Hadoop/Spark 组件异常。
    - 提供详细的诊断报告和修复建议。
3.  **全链路日志分析 (Log Analysis)**
    - 支持系统日志、执行日志和操作日志的多维度检索。
    - 提供高亮显示和日志下载功能。
4.  **企业级安全 (Enterprise Security)**
    - 完善的 RBAC（基于角色的访问控制）权限体系。
    - 基于 JWT 的双 Token 认证机制（Access + Refresh）。

### 🛠 安装指南

**前置要求：**
- Node.js >= 18.0.0
- pnpm (推荐) 或 npm/yarn

1.  **克隆项目**
    ```bash
    git clone <repository-url>
    cd project
    ```

2.  **进入前端目录**
    本项目核心代码位于 `frontend-vue` 目录下：
    ```bash
    cd frontend-vue
    ```

3.  **安装依赖**
    ```bash
    pnpm install
    ```

### 💻 使用说明

**1. 启动开发服务器**
```bash
pnpm dev
```
启动后访问 `http://localhost:5173` 即可预览项目。

**2. 构建生产环境代码**
```bash
pnpm build
```
构建产物将输出到 `dist/` 目录，可直接部署到 Nginx 或其他 Web 服务器。

**3. 运行测试**
- **单元测试**:
  ```bash
  pnpm test
  ```
- **端到端测试 (E2E)**:
  ```bash
  pnpm e2e
  ```

**4. 代码检查与格式化**
```bash
pnpm lint      # 检查代码
pnpm lint:fix  # 自动修复格式问题
```

### 📂 目录结构

```text
/home/devbox/project/
├── frontend-vue/             # 前端项目主目录
│   ├── src/
│   │   ├── api/              # API 接口服务
│   │   ├── components/       # 公共 UI 组件 (图表, 日志查看器等)
│   │   ├── views/            # 页面视图 (仪表盘, 诊断页, 登录页)
│   │   ├── stores/           # Pinia 状态管理 (用户认证, 全局状态)
│   │   ├── router/           # 路由配置与权限守卫
│   │   ├── lib/              # 工具库 (ECharts配置, 遥测埋点)
│   │   ├── App.vue           # 根组件
│   │   └── main.ts           # 程序入口
│   ├── tests/                # 单元测试文件
│   ├── e2e/                  # E2E 测试文件
│   ├── public/               # 静态资源
│   ├── vite.config.ts        # Vite 配置文件
│   └── package.json          # 项目依赖配置
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
**Enterprise Cluster Management Console** is a high-performance web application built with a modern frontend tech stack (Vue 3 + TypeScript + Vite). Designed for big data operations teams, it provides a one-stop solution for cluster monitoring, log analysis, and fault diagnosis. With intuitive visualizations, it helps users track cluster health in real-time and quickly troubleshoot system anomalies.

**Tech Stack:**
- **Framework**: Vue.js 3 (Composition API)
- **Language**: TypeScript
- **Build Tool**: Vite
- **UI Library**: Element Plus
- **State Management**: Pinia
- **Charting**: ECharts
- **Testing**: Vitest (Unit) + Playwright (E2E)

### ✨ Features
1.  **Visual Monitoring (Dashboard)**
    - Real-time display of cluster node status (Health/Warning/Down).
    - Dynamic rendering of CPU and Memory usage trends.
2.  **Intelligent Diagnosis**
    - Built-in automated diagnostic tools to detect Hadoop/Spark component anomalies with one click.
    - Provides detailed diagnostic reports and repair suggestions.
3.  **Full-Link Log Analysis**
    - Multi-dimensional search for system logs, execution logs, and operation logs.
    - Syntax highlighting and log download capabilities.
4.  **Enterprise Security**
    - Comprehensive RBAC (Role-Based Access Control) system.
    - JWT-based dual token authentication mechanism (Access + Refresh).

### 🛠 Installation

**Prerequisites:**
- Node.js >= 18.0.0
- pnpm (recommended) or npm/yarn

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd project
    ```

2.  **Navigate to Frontend Directory**
    The core code is located in the `frontend-vue` directory:
    ```bash
    cd frontend-vue
    ```

3.  **Install Dependencies**
    ```bash
    pnpm install
    ```

### 💻 Usage

**1. Start Development Server**
```bash
pnpm dev
```
Access `http://localhost:5173` to preview the application.

**2. Build for Production**
```bash
pnpm build
```
The output will be generated in the `dist/` directory, ready for deployment to Nginx or other web servers.

**3. Run Tests**
- **Unit Tests**:
  ```bash
  pnpm test
  ```
- **E2E Tests**:
  ```bash
  pnpm e2e
  ```

**4. Linting**
```bash
pnpm lint      # Check code quality
pnpm lint:fix  # Auto-fix formatting issues
```

### 📂 Directory Structure

```text
/home/devbox/project/
├── frontend-vue/             # Main frontend project directory
│   ├── src/
│   │   ├── api/              # API services
│   │   ├── components/       # Shared UI components (Charts, LogViewer)
│   │   ├── views/            # Page views (Dashboard, Diagnosis, Login)
│   │   ├── stores/           # Pinia state management (Auth, Global)
│   │   ├── router/           # Router config & permission guards
│   │   ├── lib/              # Utilities (ECharts config, Telemetry)
│   │   ├── App.vue           # Root component
│   │   └── main.ts           # Application entry point
│   ├── tests/                # Unit test files
│   ├── e2e/                  # E2E test files
│   ├── public/               # Static assets
│   ├── vite.config.ts        # Vite configuration
│   └── package.json          # Project dependencies
└── README.md                 # Project documentation
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
