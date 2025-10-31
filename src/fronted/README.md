# 集群管理系统前端项目

基于 Hadoop 的集群管理系统前端界面，提供集群状态监控、日志查询、故障诊断和自动修复功能。

## 项目结构

```
src/fronted/
├── index.html              # 主页面文件（重构后）
├── 原型图.html             # 原始原型文件（已优化）
├── assets/                 # 静态资源目录
│   ├── images/            # 图片资源
│   ├── fonts/             # 字体文件
│   └── icons/             # 图标文件
├── components/            # 可复用组件
│   ├── common/           # 通用组件
│   ├── layout/           # 布局组件
│   └── ui/               # UI 组件
├── styles/               # 样式文件
│   ├── base/            # 基础样式
│   │   ├── reset.css    # CSS 重置
│   │   └── variables.css # CSS 变量
│   ├── components/      # 组件样式
│   │   ├── header.css   # 头部样式
│   │   ├── sidebar.css  # 侧边栏样式
│   │   ├── dashboard.css # 仪表板样式
│   │   └── buttons.css  # 按钮样式
│   ├── layouts/         # 布局样式
│   │   ├── main.css     # 主布局
│   │   └── responsive.css # 响应式布局
│   ├── utils/           # 工具样式
│   │   └── utilities.css # 原子类
│   └── main.css         # 主样式文件
├── utils/               # 工具函数
│   ├── charts.js        # 图表管理
│   ├── navigation.js    # 导航管理
│   └── responsive.js    # 响应式交互
└── views/               # 页面级组件
```

## 功能特性

### 🎯 核心功能
- **集群状态监控**: 实时显示节点状态、CPU、内存使用情况
- **日志查询**: 支持多条件筛选的日志查询功能
- **故障诊断**: 自动检测和诊断系统故障
- **自动修复**: 提供故障修复建议和自动修复功能

### 🎨 设计规范
- **HTML5 语义化**: 使用 `<header>`, `<nav>`, `<main>`, `<aside>`, `<section>`, `<article>` 等语义化标签
- **BEM 命名规范**: 所有 CSS 类名遵循 BEM (Block Element Modifier) 命名规范
- **CSS 模块化**: 样式按功能模块拆分，便于维护和复用
- **响应式设计**: 支持桌面端、平板端和移动端适配

### 📱 响应式特性
- **移动端优先**: 采用移动端优先的响应式设计策略
- **断点设计**: 
  - 移动端: ≤ 768px
  - 平板端: 769px - 1024px  
  - 桌面端: ≥ 1025px
- **触摸手势**: 支持滑动手势操作侧边栏
- **自适应布局**: 图表、表格、卡片等组件自动适配不同屏幕尺寸

### ♿ 无障碍访问
- **ARIA 标签**: 完整的 ARIA 属性支持
- **键盘导航**: 支持 Tab 键和 ESC 键操作
- **屏幕阅读器**: 兼容主流屏幕阅读器
- **焦点管理**: 清晰的焦点指示和管理

## 技术栈

- **HTML5**: 语义化标签和现代 Web 标准
- **CSS3**: Flexbox、Grid、CSS Variables、媒体查询
- **JavaScript ES6+**: 模块化、类、箭头函数等现代语法
- **ECharts**: 数据可视化图表库
- **Font Awesome**: 图标库
- **Tailwind CSS**: 原子化 CSS 框架（临时保留）

## 开发规范

### CSS 规范
- **选择器特异性**: 不超过 3 级嵌套
- **BEM 命名**: 严格遵循 BEM 命名规范
- **CSS 变量**: 使用 CSS 自定义属性管理设计系统
- **模块化**: 按功能拆分 CSS 文件

### JavaScript 规范
- **ES6+ 语法**: 使用现代 JavaScript 语法
- **模块化**: 功能按模块拆分
- **类设计**: 使用 ES6 类组织代码
- **事件管理**: 统一的事件绑定和解绑

### HTML 规范
- **语义化**: 使用合适的 HTML5 语义化标签
- **无障碍**: 完整的 ARIA 属性和无障碍支持
- **SEO 友好**: 合理的 meta 标签和结构化数据

## 快速开始

### 1. 启动开发服务器

```bash
cd /home/devbox/project/src/fronted
python3 -m http.server 8080
```

### 2. 访问应用

打开浏览器访问: `http://localhost:8080/index.html`

### 3. 功能测试

- **导航切换**: 点击顶部导航项切换不同页面
- **响应式测试**: 调整浏览器窗口大小测试响应式布局
- **移动端测试**: 使用浏览器开发者工具模拟移动设备
- **无障碍测试**: 使用 Tab 键测试键盘导航

## 浏览器兼容性

- **现代浏览器**: Chrome 60+, Firefox 60+, Safari 12+, Edge 79+
- **移动浏览器**: iOS Safari 12+, Chrome Mobile 60+
- **特性支持**: CSS Grid, Flexbox, CSS Variables, ES6+

## 性能优化

- **CSS 优化**: 模块化加载，减少重复样式
- **JavaScript 优化**: 按需加载，事件委托
- **图片优化**: 使用 SVG 矢量图标
- **缓存策略**: 合理的资源缓存设置

## 维护说明

### 添加新页面
1. 在 `views/` 目录创建页面组件
2. 在 `styles/components/` 添加对应样式
3. 在 `utils/navigation.js` 中添加路由逻辑

### 添加新组件
1. 在 `components/` 对应目录创建组件
2. 在 `styles/components/` 添加组件样式
3. 遵循 BEM 命名规范

### 样式修改
1. 优先修改 CSS 变量 (`styles/base/variables.css`)
2. 组件样式修改对应的组件 CSS 文件
3. 确保响应式适配正常

## 部署说明

### 生产环境部署
1. 移除 Tailwind CSS CDN 引用
2. 压缩 CSS 和 JavaScript 文件
3. 配置适当的 HTTP 缓存头
4. 启用 Gzip 压缩

### 静态资源优化
- 图片压缩和格式优化
- CSS 和 JavaScript 文件合并压缩
- 字体文件子集化
- CDN 资源配置

## 更新日志

### v2.0.0 (2023-10-15)
- ✨ 完全重构项目结构
- ✨ 实现 HTML5 语义化标签
- ✨ 采用 BEM 命名规范
- ✨ 模块化 CSS 架构
- ✨ 响应式布局支持
- ✨ 无障碍访问优化
- ✨ 现代 JavaScript 重构

### v1.0.0 (2023-10-01)
- 🎉 初始版本发布
- 📊 基础仪表板功能
- 🔍 日志查询功能
- 🔧 故障诊断功能
- 🛠️ 自动修复功能

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交代码变更
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License - 详见 LICENSE 文件