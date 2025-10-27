# ErrorDetecting 前端项目

## 项目简介

ErrorDetecting 是一个分布式系统错误检测与监控平台的前端应用，提供直观的用户界面来监控系统状态、管理故障和分析日志。

## 功能特性

- 🎯 **概览仪表板** - 系统整体运行状态概览
- 🖥️ **集群监控** - 实时监控集群节点状态和性能指标
- 🚨 **故障管理** - 故障报告、处理和跟踪管理
- 📊 **日志分析** - 日志查询、分析和可视化
- 👤 **用户管理** - 用户权限和角色管理
- ⚙️ **系统配置** - 系统参数和配置管理
- 📱 **响应式设计** - 支持多种设备和屏幕尺寸

## 技术栈

- **HTML5** - 页面结构
- **CSS3** - 样式设计，包含响应式布局
- **JavaScript (ES6+)** - 交互逻辑和数据处理
- **Chart.js** - 数据可视化图表
- **Font Awesome** - 图标库

## 项目结构

```
frontend/
├── index.html              # 主页面入口
├── styles/                 # 样式文件目录
│   ├── main.css           # 主样式文件
│   ├── login.css          # 登录页面样式
│   ├── cluster-monitor.css # 集群监控页面样式
│   ├── fault-manage.css   # 故障管理页面样式
│   ├── log-analysis.css   # 日志分析页面样式
│   ├── components.css     # 通用组件样式
│   └── responsive.css     # 响应式设计样式
├── js/                    # JavaScript文件目录
│   ├── app.js            # 主应用逻辑
│   ├── components.js     # 通用组件库
│   ├── charts.js         # 图表组件库
│   └── demo-data.js      # 演示数据管理
├── views/                 # 页面视图目录
├── components/           # 可复用组件
├── api/                  # API接口封装
├── utils/                # 工具函数
├── router/               # 路由配置
└── README.md            # 项目说明文档
```

## 快速开始

### 1. 环境要求

- 现代浏览器 (Chrome, Firefox, Safari, Edge)
- Python 3.x (用于本地开发服务器)

### 2. 启动项目

```bash
# 进入前端目录
cd src/frontend

# 启动本地HTTP服务器
python -m http.server 8080

# 或者使用Node.js
npx http-server -p 8080
```

### 3. 访问应用

打开浏览器访问: http://localhost:8080

### 4. 默认登录信息

- 用户名: admin
- 密码: admin123

## 页面功能说明

### 概览仪表板
- 显示系统整体运行状态
- 在线节点数量、活跃告警、资源使用率等关键指标
- 系统性能趋势图表

### 集群监控
- 实时监控所有节点状态
- 节点性能指标 (CPU、内存、磁盘使用率)
- 节点管理操作 (重启、停止、详情查看)
- 资源使用趋势分析

### 故障管理
- 故障列表查看和筛选
- 故障详情查看和处理
- 故障统计和分析
- 故障报告导出

### 日志分析
- 多条件日志查询
- 日志级别和服务筛选
- 日志趋势分析图表
- 实时日志监控

## 组件库

### 通用组件
- **Modal** - 模态框组件
- **Loading** - 加载动画组件
- **Notification** - 通知组件
- **Confirm** - 确认对话框
- **Alert** - 提示框
- **Tooltip** - 工具提示
- **Dropdown** - 下拉菜单

### 图表组件
- **LineChart** - 线性图表
- **BarChart** - 柱状图表
- **PieChart** - 饼图
- **DoughnutChart** - 环形图
- **RealTimeChart** - 实时图表

## 响应式设计

项目采用响应式设计，支持以下设备：

- 📱 **移动设备** (< 480px)
- 📱 **小屏平板** (480px - 767px)
- 💻 **中等屏幕** (768px - 1023px)
- 🖥️ **大屏幕** (1024px - 1199px)
- 🖥️ **超大屏幕** (≥ 1200px)

## 浏览器支持

- Chrome ≥ 60
- Firefox ≥ 55
- Safari ≥ 12
- Edge ≥ 79

## 开发指南

### 添加新页面

1. 在 `views/` 目录下创建页面文件夹
2. 创建对应的HTML和CSS文件
3. 在 `app.js` 中添加路由配置
4. 在侧边栏导航中添加菜单项

### 使用组件

```javascript
// 显示通知
Notification.show('操作成功', 'success');

// 显示确认对话框
const result = await Confirm.show('确定要删除吗？');

// 创建图表
const chart = ChartFactory.createLineChart('chartCanvas', data);
```

### 获取演示数据

```javascript
// 获取仪表板数据
const dashboardData = demoData.getDashboardData();

// 搜索故障
const faults = demoData.searchFaults('CPU', { level: 'critical' });

// 获取实时数据
const realtimeData = demoData.getRealtimeData();
```

## 部署说明

### 生产环境部署

1. 将所有文件上传到Web服务器
2. 配置Web服务器支持SPA路由
3. 确保所有静态资源可正常访问
4. 配置HTTPS (推荐)

### Nginx配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/frontend;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 性能优化

- 使用CDN加载第三方库
- 启用Gzip压缩
- 图片懒加载
- 代码分割和按需加载
- 缓存策略优化

## 故障排除

### 常见问题

1. **页面无法加载**
   - 检查HTTP服务器是否正常启动
   - 确认端口号是否被占用

2. **图表不显示**
   - 检查Chart.js库是否正确加载
   - 确认canvas元素是否存在

3. **样式异常**
   - 检查CSS文件路径是否正确
   - 确认浏览器是否支持CSS特性

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

本项目采用 MIT 许可证。

## 联系方式

如有问题或建议，请联系开发团队。

---

## 原始开发文档

以下是项目的原始开发文档和需求分析：

### 项目背景

在基于 Hadoop 的故障检测与自动恢复项目中，前端开发者需围绕"运维人员可视化操作入口"核心目标，从需求对齐到上线维护全流程参与，具体工作可按**项目阶段**拆解为以下详细内容，同时紧密贴合项目文档（前景与范围、用例、核心任务）中的前端相关需求：

### 一、项目前期：需求对齐与技术准备（项目启动-基础搭建阶段）
此阶段核心是明确"做什么"和"用什么做"，避免后期需求偏差，对应文档中"Web 应用功能范围""用例场景"等内容。

#### 1. 需求分析与边界确认
需与产品、后端、运维人员同步，明确前端核心功能边界，重点对齐以下内容：
- **功能范围确认**（参考《前景与范围文档》4.1 功能范围）：
  - 必做：登录、集群监控（节点状态/资源趋势）、故障管理（列表/详情/修复）、日志分析（查询/AI 提交）；
  - 不做：非 Hadoop 组件（如 Spark）的监控、跨集群管理、离线日志回溯（仅实时日志）。
- **用例场景拆解**（参考《用例文档》核心用例）：
  - 梳理每个用例的前端交互细节，例如：
    - 故障修复（UC-006）：需按风险分级展示按钮（低风险"自动修复"、中风险"确认修复"、高风险"申请审批"），并实时展示执行日志；
    - AI 日志分析（UC-008）：需限制最多勾选 10 条日志，分析超时后提示"后台继续处理，结果将推送"。
- **运维人员体验诉求**：
  - 深色主题适配（运维场景多在夜间使用，减少视觉疲劳）；
  - 操作简洁（核心功能如"修复""刷新"按钮突出，避免多层级跳转）；
  - 异常提示明确（如接口失败时需区分"集群连接中断""Token 过期"等场景）。

#### 2. 技术栈选型与版本确认
基于《核心任务说明文档》任务 5 明确的技术栈，进一步确认版本兼容性与工具链：
- **核心技术栈**（固定）：
  - 框架：Vue 3.3+（Composition API 风格，便于逻辑复用）；
  - 构建工具：Vite 4.0+（比 Webpack 快，适配 Vue 3，支持热更新）；
  - UI 组件库：Element Plus 2.3+（需支持表格、弹窗、表单，适配 Vue 3）；
  - 图表库：ECharts 5.4+（需支持折线图（CPU/磁盘趋势）、表格标注（异常节点标红））；
  - 网络请求：Axios 1.4+（处理接口拦截、Token 携带、跨域）；
- **补充工具**：
  - 代码规范：ESLint（Vue 3 规则）+ Prettier（统一格式）；
  - 样式方案：CSS 变量（实现深色/浅色主题切换）+ SCSS（嵌套样式，提高可维护性）；
  - 路由：Vue Router 4.2+（需支持 history 模式，配合 Nginx 部署）。

### 二、项目初始化：前端架构搭建（应用开发阶段前期）
此阶段需搭建可扩展的项目架构，为后续开发提效，避免后期重构。

#### 1. 项目初始化与配置
- **创建项目**：
  ```bash
  npm create vite@latest hadoop-fault-front -- --template vue  # 初始化 Vue 3 项目
  cd hadoop-fault-front && npm install  # 安装依赖
  npm install element-plus echarts axios vue-router@4  # 安装核心依赖
  ```
- **核心配置（vite.config.js）**：
  - 跨域代理（开发环境调用后端 FastAPI 接口需解决跨域）：
    ```javascript
    export default defineConfig({
      server: {
        proxy: {
          '/api': {
            target: 'http://localhost:8000',  // 后端开发环境地址
            changeOrigin: true,  // 允许跨域
            rewrite: (path) => path.replace(/^\/api/, '')  // 去掉请求路径中的 /api 前缀
          }
        }
      },
      resolve: {
        alias: {
          '@': path.resolve(__dirname, 'src')  // 路径别名，@ 指向 src 目录
        }
      }
    })
    ```
  - 环境变量：创建 `.env.development`（开发环境）和 `.env.production`（生产环境），配置 API 基础地址：
    ```env
    # .env.development
    VITE_API_BASE_URL = '/api'  # 开发环境（走代理）
    # .env.production
    VITE_API_BASE_URL = 'http://生产后端IP:8000'  # 生产环境（直接调用后端）
    ```

### 2. 目录结构设计（按功能拆分，便于维护）
```
frontend/
├── api/          # 接口请求封装（按模块拆分）
│   ├── user.js   # 登录、退出接口
│   ├── cluster.js# 集群状态接口
│   ├── fault.js  # 故障管理接口
│   └── log.js    # 日志查询、AI 分析接口
├── components/   # 公共组件（复用性强）
│   ├── Layout/   # 页面布局（侧边栏+顶部栏）
│   ├── Common/   # 通用组件（加载动画、错误弹窗、确认弹窗）
│   └── Chart/    # 图表组件（CPU/磁盘趋势图、异常节点表格）
├── views/        # 核心页面（按功能模块拆分）
│   ├── Login/    # 登录页
│   ├── ClusterMonitor/  # 集群监控页
│   ├── FaultManage/     # 故障管理页（列表+详情）
│   └── LogAnalysis/     # 日志分析页
├── router/       # 路由配置
│   └── index.js  # 路由规则（含权限守卫）
├── utils/        # 工具函数
│   ├── request.js# Axios 实例封装（拦截器、错误处理）
│   ├── format.js # 时间格式化、日志筛选等工具
│   └── auth.js   # Token 存储/获取/删除
├── styles/       # 全局样式
│   ├── main.scss # 全局样式入口（引入 Element Plus 主题、CSS 变量）
│   └── dark.scss # 深色主题样式
└── App.vue       # 根组件（路由出口）
```


## 三、核心开发：公共组件与页面实现（应用开发阶段中期）
此阶段需优先开发公共组件（复用），再实现核心页面，严格贴合用例场景与交互需求。

### 1. 公共组件开发（优先完成，减少重复代码）
#### （1）基础布局组件（src/components/Layout/Index.vue）
- **功能**：包含侧边栏（导航菜单）、顶部栏（用户信息、刷新、退出），适配所有页面；
- **关键实现**：
  - 侧边栏菜单：按“集群监控→故障管理→日志分析”排序（运维高频操作优先），用 Element Plus 的 `ElMenu` 组件；
  - 顶部栏：显示当前登录用户（从 localStorage 获取），“退出”按钮触发清除 Token 并跳转登录页；
  - 深色主题切换：用 Element Plus 的 `ElSwitch` 控制 `document.documentElement.classList` 切换 `dark` 类，配合 CSS 变量生效。

#### （2）通用工具组件
- **加载组件（src/components/Common/Loading.vue）**：
  - 场景：接口请求时显示（如集群状态加载、AI 分析中）；
  - 实现：用 Element Plus 的 `ElLoading` 或自定义全屏加载动画，支持传入“加载文案”（如“AI 分析中，约 30 秒”）。
- **错误弹窗组件（src/components/Common/ErrorTip.vue）**：
  - 场景：接口请求失败（如集群连接中断、Token 过期）；
  - 实现：封装 Element Plus 的 `ElMessage`，支持区分错误类型（网络错误→“请检查网络”；业务错误→后端返回的错误信息）。
- **确认弹窗组件（src/components/Common/Confirm.vue）**：
  - 场景：中风险故障修复、账号禁用等需确认的操作；
  - 实现：封装 Element Plus 的 `ElMessageBox`，支持传入“标题”“内容”“确认按钮文案”，返回 Promise 便于后续处理。

#### （3）图表组件（src/components/Chart/ResourceTrend.vue）
- **功能**：展示节点 CPU/磁盘使用率趋势（用 ECharts 折线图）；
- **关键实现**：
  - 数据适配：接收后端返回的“时间轴+使用率数组”，格式化为 ECharts 所需的 `xAxis.data` 和 `series.data`；
  - 异常标注：当使用率超过阈值（如磁盘 85%）时，用 ECharts 的 `markLine` 画红色警戒线，并标注“告警阈值”；
  - 懒加载：用 Vue 的 `v-intersect` 指令（需安装 `@vueuse/core`），滚动到图表区域才初始化，减少首屏加载时间。

### 2. 核心页面实现（按用例优先级开发，高优先级先做）
#### （1）登录页（src/views/Login/Index.vue，用例 UC-001）
- **功能**：账号密码验证，对接后端 `/api/user/login` 接口；
- **关键实现**：
  - 表单验证：用 Element Plus 的 `ElForm` 做规则校验（账号不能为空、密码≥6 位且含特殊字符）；
  - Token 处理：登录成功后，将后端返回的 Token 存入 localStorage（如 `localStorage.setItem('token', res.data.token)`），并跳转首页（`router.push('/cluster-monitor')`）；
  - 异常处理：账号禁用→提示“账号已禁用，请联系管理员”；密码错误→提示“账号或密码错误”（后端返回对应的错误码，前端匹配处理）。

#### （2）集群监控页（src/views/ClusterMonitor/Index.vue，用例 UC-002、UC-003）
- **功能**：展示节点列表（状态、角色、资源使用率）、CPU/磁盘趋势图，定时 5 分钟刷新；
- **关键实现**：
  - 节点列表：用 Element Plus 的 `ElTable`，按“角色”分组（NameNode、DataNode），异常状态标注（离线→标红、磁盘>90%→标橙）；
  - 资源趋势图：复用 `ResourceTrend` 组件，支持切换“CPU/磁盘”指标，默认显示近 24 小时数据；
  - 定时刷新：用 `setInterval` 每 5 分钟调用 `getClusterStatus` 接口，页面离开时用 `onUnmounted` 清除定时器（避免内存泄漏）；
  - 手动刷新：“刷新”按钮触发接口调用，加载期间显示 `Loading` 组件。

#### （3）故障管理页（分列表和详情，用例 UC-004、UC-005、UC-006）
##### ① 故障列表页（src/views/FaultManage/List.vue）
- **功能**：按“未修复/已修复”筛选故障，展示故障 ID、类型、发生时间、风险等级；
- **关键实现**：
  - 筛选功能：用 Element Plus 的 `ElSelect` 实现状态筛选，筛选后重新调用 `/api/fault/list` 接口（携带筛选参数）；
  - 分页：用 Element Plus 的 `ElPagination`，支持切换“每页条数”（10/20/50），分页参数同步到接口请求；
  - 跳转详情：点击表格行，携带故障 ID 跳转详情页（`router.push(/fault-detail/${faultId})`）。

##### ② 故障详情页（src/views/FaultManage/Detail.vue）
- **功能**：展示故障日志、诊断结果、修复脚本，按风险等级显示修复按钮，实时展示修复日志；
- **关键实现**：
  - 数据加载：页面初始化时，通过路由参数 `route.params.faultId` 调用 `/api/fault/detail` 接口，加载故障信息；
  - 风险分级按钮：
    - 低风险：直接显示“自动修复”按钮，点击调用 `/api/fault/execute` 接口；
    - 中风险：显示“确认修复”按钮，点击触发 `Confirm` 组件，确认后执行修复；
    - 高风险：显示“申请审批”按钮，点击后提示“已发送审批请求，等待管理员确认”（后续通过 WebSocket 接收审批结果）；
  - 实时日志：修复过程中，用 `ElTag` 或 `ElText` 实时渲染后端返回的执行日志（接口返回 `stream` 流或通过 WebSocket 推送）；
  - 状态同步：修复完成后，自动更新故障状态（“未修复”→“已修复”），并提示“修复成功”，提供“返回列表”按钮。

#### （4）日志分析页（src/views/LogAnalysis/Index.vue，用例 UC-007、UC-008）
- **功能**：按“时间范围/节点/日志级别”查询日志，支持勾选日志提交 AI 分析；
- **关键实现**：
  - 查询表单：用 Element Plus 的 `ElDatePicker`（时间范围）、`ElSelect`（节点/日志级别），“查询”按钮触发 `/api/log/query` 接口；
  - 日志列表：用 `ElTable` 展示结构化日志（时间戳、级别、组件、内容），支持勾选（限制最多 10 条，超过提示“最多勾选 10 条日志”）；
  - AI 分析：
    - 点击“提交 AI 分析”，携带勾选的日志 ID 调用 `/api/llm/diagnose` 接口；
    - 分析中显示 `Loading` 组件，超时（>30 秒）提示“分析超时，已后台继续处理，结果将推送”；
    - 分析成功后，弹窗展示诊断结果（故障类型、原因、修复脚本），提供“前往故障详情”按钮。

### 3. 接口请求封装（src/utils/request.js + src/api/模块.js）
- **第一步：Axios 实例封装（src/utils/request.js）**：
  - 处理请求头：自动携带 Token（从 localStorage 获取）；
  - 响应拦截：处理 401（Token 过期→清除 Token 并跳转登录）、500（服务器错误→提示“服务器异常，请重试”）；
  ```javascript
  import axios from 'axios';
  import { ElMessage } from 'element-plus';
  import router from '@/router';

  const service = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    timeout: 30000  // AI 分析接口超时设为 30 秒
  });

  // 请求拦截器：加 Token
  service.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // 响应拦截器：处理错误
  service.interceptors.response.use(
    (response) => response.data,  // 直接返回响应体
    (error) => {
      if (error.response?.status === 401) {
        // Token 过期：清除数据并跳转登录
        localStorage.removeItem('token');
        router.push('/login');
        ElMessage.error('登录已过期，请重新登录');
      } else {
        ElMessage.error(error.message || '请求失败，请重试');
      }
      return Promise.reject(error);
    }
  );

  export default service;
  ```
- **第二步：按模块封装接口（如 src/api/fault.js）**：
  ```javascript
  import request from '@/utils/request';

  // 获取故障列表
  export const getFaultList = (params) => {
    return request({
      url: '/fault/list',
      method: 'get',
      params  // 筛选参数（status: 'unfixed'/'fixed'）
    });
  };

  // 执行故障修复
  export const executeFaultFix = (faultId) => {
    return request({
      url: `/fault/execute`,
      method: 'post',
      data: { faultId }
    });
  };
  ```


## 四、联调与优化：接口联调与性能优化（应用开发阶段后期）
此阶段需与后端紧密配合，解决接口问题，并优化页面性能与体验。

### 1. 接口联调（核心：对齐数据格式，解决交互问题）
- **联调准备**：与后端确认每个接口的“请求参数格式”“响应数据结构”（如故障列表接口返回 `{ code: 200, data: { list: [], total: 100 } }`）；
- **关键场景联调**：
  - 集群状态接口：确认返回的“节点状态”字段（如 `status: 'online'/'offline'`），确保表格标注正确；
  - 故障修复接口：确认“执行日志”的返回方式（stream 流→前端用 `onDownloadProgress` 实时接收；WebSocket→建立连接监听推送）；
  - AI 分析接口：确认“超时处理”逻辑（后端是否支持异步推送，前端是否需要轮询查询结果）；
- **问题记录**：用文档记录联调中的问题（如“故障详情接口缺少‘修复脚本’字段”），同步后端修复，避免遗漏。

### 2. 性能与体验优化（贴合任务 8 中的“前端优化”要求）
- **首屏加载优化**：
  - 路由懒加载：在 `src/router/index.js` 中用 `() => import('@/views/xxx')` 实现，减少首屏 JS 体积；
  ```javascript
  const routes = [
    {
      path: '/cluster-monitor',
      name: 'ClusterMonitor',
      component: () => import('@/views/ClusterMonitor/Index.vue')  // 懒加载
    }
  ];
  ```
  - 图表懒加载：非首屏图表（如日志分析页的趋势图）用 `v-intersect` 指令，滚动到可视区域才初始化；
- **接口请求优化**：
  - 缓存高频接口：如集群状态接口（5 分钟刷新），用 `localStorage` 缓存上次请求结果，避免重复调用；
  - 合并重复请求：用 Axios 拦截器实现“同一接口未返回时，不重复发起请求”（如多次点击“刷新”按钮）；
- **兼容性优化**：
  - 浏览器兼容：测试 Chrome 90+、Firefox 90+（项目要求），修复 CSS 兼容性问题（如 Flex 布局、CSS 变量）；
  - 响应式适配：用 Element Plus 的 `Layout` 组件和媒体查询，确保 1366px+ 屏幕正常显示（运维多使用台式机）。


## 五、部署与维护：构建部署与上线后迭代（落地保障阶段）
此阶段需配合运维完成部署，并处理上线后的问题与迭代需求。

### 1. 项目构建与部署（贴合任务 9 中的“容器化部署”）
#### （1）构建生产包
- 执行 `npm run build` 生成 `dist` 目录（生产环境代码，已压缩混淆）；
- 检查 `dist` 目录结构（确保 `index.html` 正确引用 JS/CSS 文件）。

#### （2）编写 Docker 相关文件（配合运维容器化部署）
- **Dockerfile（前端镜像构建）**：
  ```dockerfile
  # 基础镜像：Nginx（轻量，适合静态资源部署）
  FROM nginx:alpine

  # 复制构建好的 dist 目录到 Nginx 的 html 目录
  COPY dist /usr/share/nginx/html

  # 复制 Nginx 配置文件（解决路由 history 模式和反向代理）
  COPY nginx.conf /etc/nginx/conf.d/default.conf

  # 暴露 80 端口（与 Nginx 配置一致）
  EXPOSE 80

  # 启动 Nginx（前台运行）
  CMD ["nginx", "-g", "daemon off;"]
  ```
- **nginx.conf（Nginx 配置）**：
  ```nginx
  server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # 反向代理：将 /api 请求转发到后端服务（容器名+端口，由 docker-compose 管理）
    location /api {
      proxy_pass http://backend:8000;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
    }

    # 解决 Vue Router history 模式的 404 问题（所有路由指向 index.html）
    location / {
      try_files $uri $uri/ /index.html;
    }
  }
  ```
- **配合运维**：将 `dist`、`Dockerfile`、`nginx.conf` 交给运维，由运维通过 `docker-compose` 与后端、MySQL、Redis 等服务一起部署。

### 2. 上线后维护与迭代（贴合任务 10 中的“持续改进”）
- **问题排查**：
  - 生产环境 bug：通过浏览器“开发者工具”查看控制台错误（如接口 500、JS 报错），配合后端定位问题（如“日志分析页勾选超过 10 条未提示”→前端补充判断逻辑）；
  - 兼容性问题：收集运维反馈（如 Firefox 中图表不显示），修复 ECharts 初始化问题；
- **需求迭代**：
  - 低优先级需求：如“日志导出 Excel”（任务 6 中未提及，属于迭代需求），用 Element Plus 的 `XLSX` 库实现；
  - 体验优化：如“故障列表页增加‘最近 24 小时’筛选”，根据运维反馈补充筛选条件；
- **文档更新**：
  - 维护前端开发文档，记录“接口变更历史”“新增功能说明”，方便后续迭代；
  - 向运维提供“前端部署手册”，说明如何更新前端镜像、重启容器。


## 六、关键注意事项（贯穿全流程）
1. **安全问题**：
   - Token 安全：避免用 `sessionStorage`（页面刷新丢失），用 `localStorage` 可配合简单加密（如 base64）；
   - XSS 防护：渲染日志内容时用 `v-text` 而非 `v-html`，避免注入恶意脚本；
2. **可维护性**：
   - 代码规范：严格遵守 ESLint 规则，提交代码前用 `npm run lint` 修复格式问题；
   - 注释清晰：组件和接口函数需加注释（如 `// 执行故障修复：传入故障ID，返回修复结果`）；
3. **运维体验**：
   - 操作反馈：所有用户操作（点击按钮、筛选）需有明确反馈（如按钮 loading、筛选后表格加载中）；
   - 异常兜底：接口返回空数据时（如无故障记录），显示“暂无数据”而非空白页面，提升运维信心。


通过以上全流程工作，前端开发者可完成“从需求到上线”的闭环，最终交付一个符合运维需求、体验流畅、稳定可靠的可视化操作系统，助力 Hadoop 集群故障的自动化处理。