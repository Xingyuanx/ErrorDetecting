# Frontend Vue Project

> **项目负责人**: 邢远鑫  
> **技术栈**: Vue.js 3.x + TypeScript + Vite + Element Plus  
> **状态**: 🚀 Active Development

## 1. 项目概述 (Project Overview)

**Frontend Vue** 是一个基于现代化前端技术栈构建的企业级集群管理与诊断平台控制台。该项目旨在为大数据运维团队提供高效、直观的图形化界面，用于监控集群状态、分析执行日志以及进行故障自动化诊断。

### 核心价值

- **可视化监控**: 实时展示集群节点状态、资源利用率及关键性能指标。
- **智能诊断**: 集成自动化诊断工具，快速定位 Hadoop/Spark 等组件的运行异常。
- **日志分析**: 提供强大的日志检索与分析界面，支持多维度过滤。
- **安全可控**: 完善的 RBAC 权限体系，确保操作安全。

---

## 2. 项目结构说明 (Project Structure)

本项目采用模块化的目录结构，核心逻辑收敛于 `src/app`，确保关注点分离。

```text
frontend-vue/
├── public/                  # 静态资源 (favicon, robots.txt)
├── src/
│   └── app/                 # 应用核心代码
│       ├── api/             # API 接口定义与服务封装
│       ├── components/      # 全局公共组件
│       ├── composables/     # Vue Composables (组合式函数)
│       ├── constants/       # 常量定义 (枚举, 配置)
│       ├── lib/             # 核心工具库 (Axios 封装, 遥测, 工具函数)
│       ├── locales/         # i18n 国际化资源
│       ├── router/          # 路由配置与权限守卫
│       ├── stores/          # Pinia 状态管理仓库
│       ├── styles/          # 全局样式 (SASS/CSS)
│       ├── types/           # TypeScript 类型定义
│       ├── views/           # 页面视图 (按业务模块划分)
│       ├── App.vue          # 根组件
│       └── main.ts          # 应用入口
├── tests/                   # 测试文件目录
├── e2e/                     # E2E 测试用例 (Playwright)
├── scripts/                 # 构建与辅助脚本
├── .eslintrc.cjs            # ESLint 配置
├── index.html               # 入口 HTML
├── package.json             # 项目依赖与脚本
├── pnpm-lock.yaml           # 依赖锁定文件
├── tsconfig.json            # TypeScript 配置
├── vite.config.ts           # Vite 构建配置
└── vitest.config.ts         # Vitest 测试配置
```

### 核心配置文件

- **`vite.config.ts`**: 配置了路径别名 (`@/`), API 代理, 生产环境分包策略 (Manual Chunks) 及 CSS 预处理。
- **`tsconfig.json`**: TypeScript 严格模式配置，目标版本 ES2020。
- **`playwright.config.ts`**: 端到端测试的浏览器与运行环境配置。

---

## 3. 开发环境配置 (Development Setup)

### 前置要求

- **Node.js**: `>=18.12.0` (推荐 LTS 版本)
- **包管理器**: `pnpm` (本项目强制使用 pnpm 以确保依赖一致性)
- **操作系统**: macOS / Linux / Windows (WSL2 推荐)

### 环境变量

项目使用 `.env` 文件体系管理环境变量。请在根目录创建 `.env.local`用于本地开发覆盖：

```properties
# .env (默认配置)
VITE_API_TARGET=http://localhost:8000
VITE_DEV_HOST=0.0.0.0
VITE_TELEMETRY_ENABLED=true
VITE_AUTH_REFRESH_ENABLED=true
```

### IDE 推荐配置 (VS Code)

建议安装以下插件以获得最佳开发体验：

- **Vue - Official (Volar)**: 必须安装，提供 Vue 3 语法支持。
- **ESLint**: 代码质量检查。
- **Prettier - Code formatter**: 代码格式化。
- **Tailwind CSS IntelliSense**: 如果项目中引入了 Tailwind。
- **EditorConfig for VS Code**: 保持跨编辑器风格一致。

---

## 4. 开发指南 (Development Guide)

### 4.1 初始化项目

```bash
# 安装依赖
pnpm install

# 检查环境健康度
pnpm run typecheck
```

### 4.2 启动开发服务器

```bash
pnpm dev
# 默认运行在 http://localhost:5173
```

### 4.3 代码规范与质量

项目集成了严格的代码规范检查：

- **Lint**: `pnpm run lint` (检查代码质量)
- **Fix**: `pnpm run lint:fix` (自动修复简单错误)
- **Type Check**: `pnpm run typecheck` (TypeScript 类型检查)

### 4.4 Git 提交规范

建议遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat`: 新功能
- `fix`: 修复 Bug
- `docs`: 文档变更
- `style`: 格式调整 (不影响逻辑)
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关

---

## 5. 构建与部署 (Build & Deploy)

### 5.1 生产环境构建

```bash
pnpm build
```

构建产物将输出到 `dist/` 目录。

### 5.2 Docker 部署

项目支持容器化部署。在根目录创建 `Dockerfile`：

```dockerfile
# Build Stage
FROM node:18-alpine as builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

# Production Stage
FROM nginx:stable-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 5.3 CI/CD 流程建议

推荐使用 GitHub Actions 或 GitLab CI 实现自动化：

1. **Push 触发**: 运行 `pnpm lint` 和 `pnpm run test`。
2. **Merge 触发**: 运行构建 `pnpm build` 并推送 Docker 镜像。
3. **Release 触发**: 部署到生产环境 Kubernetes 集群。

---

## 6. 技术亮点 (Highlights)

- **🚀 极速构建**: 基于 **Vite 5**，实现毫秒级冷启动与 HMR 热更新。
- **🛡️ 企业级鉴权**:
  - 实现了基于 **JWT** 的双 Token (Access + Refresh) 认证机制。
  - Axios 拦截器自动处理 401 过期与静默刷新。
  - 细粒度的 **RBAC** 路由守卫与按钮级权限控制。
- **📊 深度可观测性**:
  - 集成 ECharts 实现复杂的数据可视化。
  - 封装 Telemetry 模块，自动采集 API 耗时与前端错误日志。
- **📦 工程化实践**:
  - 完整的 TypeScript 类型定义。
  - 统一的 API 错误处理层，将后端异常转化为友好的 UI 提示。

---

## 7. 测试方案 (Testing Strategy)

### 7.1 单元测试 (Unit Test)

使用 **Vitest** 进行组件与逻辑测试。

```bash
# 运行单元测试
pnpm test

# 监听模式
pnpm run test:watch
```

### 7.2 端到端测试 (E2E Test)

使用 **Playwright** 进行全链路测试，覆盖登录、核心业务流程。

```bash
# 运行 E2E 测试
pnpm run e2e

# 带 UI 界面运行 (调试用)
pnpm run e2e:ui
```

### 7.3 测试覆盖率

```bash
pnpm run test --coverage
```

---

_Generated for Frontend Vue Project_
