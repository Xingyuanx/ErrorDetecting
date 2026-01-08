# UI E2E（本地与 CI 稳定运行指南）

本项目使用 Playwright 进行端到端测试。

## 指令总览

在 `frontend-vue/` 目录执行：

```bash
pnpm run e2e
```

```bash
pnpm run e2e:ui
```

## CI 如何运行

CI 会自动安装浏览器与系统依赖后运行 UI E2E，并在失败时上传报告与 trace。

## 本地运行（推荐顺序）

### 方案 A：原生运行（Linux）

首次运行需要安装 Playwright 的 Chromium 及系统依赖：

```bash
pnpm run e2e:ui:install
```

之后直接运行：

```bash
pnpm run e2e:ui
```

### 方案 B：Docker 运行（最稳定）

本地没有系统依赖、或者安装依赖很慢时，推荐使用 Docker（Playwright 官方镜像已内置依赖）：

```bash
pnpm run e2e:ui:docker
```

可通过环境变量指定镜像版本：

```bash
PLAYWRIGHT_IMAGE=mcr.microsoft.com/playwright:v1.57.0-jammy pnpm run e2e:ui:docker
```

## 产物与排查

UI E2E 失败后会生成：
- `frontend-vue/playwright-report/`（HTML 报告）
- `frontend-vue/test-results/`（trace / video / screenshot）

本地查看报告：

```bash
pnpm exec playwright show-report playwright-report
```

