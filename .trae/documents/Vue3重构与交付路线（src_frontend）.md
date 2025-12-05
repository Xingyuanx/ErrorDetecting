## 项目现状概览
- 前端为静态页面与原生 JS，集中在 `src/frontend/index.html`，配套工具脚本：
  - 认证与权限：`src/frontend/utils/auth.js`
  - 导航与路由：`src/frontend/utils/navigation.js`
  - 响应式交互：`src/frontend/utils/responsive.js`
  - 图表管理：`src/frontend/utils/charts.js`
- 外部依赖通过 CDN：`Tailwind CSS`、`Font Awesome`、`Google Fonts`、`ECharts`。
- 核心页面分区（示例）：
  - 登录与注册：`index.html:164`、`index.html:210`
  - 集群列表：`index.html:254`
  - 仪表板：`index.html:374`
  - 日志查询：`index.html:573`
  - 故障诊断：`index.html:851`
  - 故障中心：`index.html:998`
  - 执行日志：`index.html:1107`
  - 告警配置：`index.html:1179`
  - 个人主页/账号：`index.html:1320`、`index.html:1355`
  - 用户与角色与权限策略/审计：`index.html:1437`、`index.html:1553`、`index.html:1592`、`index.html:1639`

## 功能与业务逻辑梳理
- 认证与权限（`auth.js`）：前端演示账密、角色驱动页面可见性与操作禁用、审批队列与用户管理占位。
- 路由与导航（`navigation.js`）：`location.hash` 单页切换、顶部/侧边/下拉菜单事件、页面切换联动日志筛选、诊断三栏、集群注册与注销、仪表板当前集群元信息。
- 响应式（`responsive.js`）：移动端菜单与侧边栏遮罩、窗口尺寸类名、触摸手势、与图表重绘联动。
- 图表（`charts.js`）：ECharts CPU 折线与内存环图初始化、更新与自适应。

## 技术栈与依赖
- 现状：原生 `HTML/CSS/JS` + CDN（`Tailwind`、`Font Awesome`、`ECharts`）。无构建工具、无包管理。
- 后端：`FastAPI` 原型（上下文参考）。目前前端非真实 API 对接。

## 核心需求与场景
- 角色驱动的集群管理：列表、仪表板、日志查阅、故障诊断与中心、告警规则管理、用户与权限管理。
- 要求：保持原有 UI 与业务流程；对接真实 API 可演进；前端可维护、可扩展。

## 重构目标与范围
- 采用 `Vue3 + Vite + Vue Router 4 + Pinia` 完整重构，迁移到 Composition API。
- 保持功能与界面一致；不做性能优化；优先可维护性与可扩展性。

## 目标目录结构（建议）
- 根：`src/`（前端工程）
  - `app/`：应用骨架
    - `main.ts`、`App.vue`
    - `router/`（路由与守卫）
    - `stores/`（Pinia 状态，如 `auth`, `clusters`, `logs`）
    - `services/`（`httpClient.ts`、API 模块）
    - `components/`（通用组件：导航、侧边栏、表格、模态框等）
    - `views/`（页面视图：登录、注册、集群列表、仪表板、日志、诊断、故障中心、告警、用户管理、角色、权限策略、审计、个人/账号）
    - `composables/`（可复用逻辑：`useResponsive`, `useCharts`, `usePagination`, `useFilters`）
    - `assets/`（样式与静态资源，复用现有 CSS）
    - `types/`（接口与实体类型定义）
  - `index.html`（Vite 模板，挂载 `#app`）

## 迁移映射与实现要点
- `auth.js` → `stores/auth.ts` + `views/Login.vue/Register.vue` + 路由守卫
  - 角色权限：在路由元信息中声明 `roles`，守卫检查；组件内用 `v-if` 控制可见性；禁用逻辑拆为指令或组件属性。
  - 审批队列/用户管理：占位列表迁移为 `views/UserManagement.vue` 与局部 `components`。
- `navigation.js` → 顶部/侧边导航组件 + `vue-router` 导航
  - 顶部导航 `HeaderNav.vue`、侧边栏 `Sidebar.vue`、系统配置下拉 `ConfigDropdown.vue`、用户菜单 `UserMenu.vue`。
  - 页面切换联动逻辑改为各 `view` 的 `onMounted/ watch(route)` 与局部 `composable`。
- `responsive.js` → `useResponsive` composable + 布局组件 `Layout.vue`
  - 移动端菜单/侧边遮罩作为 `Layout` 状态；触摸手势在同一 composable；`body` 类名通过 `onMounted` 与 `watchEffect`。
- `charts.js` → `useCharts` composable + `CpuChart.vue`、`MemoryChart.vue`
  - 统一初始化/销毁与 `resize`；数据更新通过 props 与 emits；`ECharts` 使用 npm 包并在组件中管理实例。
- `日志筛选/分页/渲染` → `views/Logs.vue` + `useLogDataset`（采集 DOM → 数据改为从 API 或本地 mock）
  - 过滤条件建立为 `reactive`；分页用 `computed` + `v-for`；摘要组件化。
- `集群注册/注销/当前集群` → `views/ClusterList.vue` + `stores/clusters.ts`，仪表板头部 `CurrentClusterMeta.vue`。
- `故障诊断三栏布局与拖拽` → `views/Diagnosis.vue` + 分栏组件与拖拽事件封装。
- `告警配置` → `views/AlertConfig.vue` + 规则表格与编辑对话框组件。

## 路由系统（Vue Router 4）
- 声明路由表：每个页面视图一个路由；嵌套路由用于主布局下的页面。
- 守卫：全局前置守卫检查登录状态与角色；未登录重定向至登录；无权限重定向至默认页（角色对应）。
- 路由元信息：`requiresAuth`、`roles`、`title`。

## 状态管理（Pinia）
- `auth`：用户信息、角色、登录/登出；持久化（`localStorage` 或 `pinia-plugin-persistedstate`）。
- `clusters`：列表、当前选中、注册/注销。
- `logs`：源数据、过滤条件、分页状态、渲染数据。
- `alerts`：规则集合与编辑状态。

## 服务层与接口对接
- `httpClient.ts`：`fetch` 或 `axios` 封装、超时/取消、错误归一化、鉴权头附加。
- API 模块：`authApi`、`clusterApi`、`logApi`、`diagnosisApi`、`alertApi`。
- 现阶段可使用 Mock（MSW 或本地 JSON）保持业务一致；后续对接后端。

## UI 保持一致
- 复用现有 CSS（复制到 `assets/styles`）；继续使用 `Font Awesome`/`Google Fonts`；保留 Tailwind（或按需移除）。
- 组件化拆分但保持样式类名与结构等效；必要时封装通用 `Table`, `Modal`, `Dropdown`。

## 测试与验收
- 单元测试：`Vitest` + `Vue Test Utils` 测组件与 store 逻辑。
- 集成测试：关键页面流程（登录/路由守卫、日志筛选与分页、集群注册/注销、告警规则增删改）。
- E2E（可选）：`Playwright` 覆盖主要用户路径。

## 交付物
- 重构后完整代码（Vue3 工程 + 视图/组件/状态/服务层）。
- 更新文档：重构变更说明、目录结构、约定与用法。
- 测试报告：通过的测试项与范围；与原有功能对齐清单。

## 实施步骤（里程碑）
1. 初始化工程（Vite + Vue3 + Router + Pinia），迁移样式与静态资源。
2. 布局与导航组件搭建，接入路由守卫与认证 store。
3. 迁移集群列表与仪表板视图与交互；ECharts 组件化。
4. 迁移日志视图（筛选/分页/摘要），抽取 composable。
5. 迁移故障诊断三栏与拖拽，联动日志预览。
6. 迁移告警配置与用户/角色/权限策略/审计页面。
7. 覆盖测试与文档编写，完成验收。

## 重构标准（遵循）
- Vue3 Composition API、单一职责组件、语义化命名与目录分层。
- 不做性能优化；聚焦等效功能与可维护性。
- 可扩展：服务层与 store 解耦，路由元信息驱动权限，组件可复用。

请确认上述计划；确认后我将开始实施，并按里程碑逐步交付可运行的 Vue3 版本与文档、测试。