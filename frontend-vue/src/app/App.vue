<template>
  <!-- 顶层模板：定义应用的根布局容器 -->
  <div class="layout">
    <!-- 侧边栏：贯穿高度，位于最左侧 -->
    <Sidebar v-if="!hideSidebar" />

    <!-- 右侧容器：包含头部导航与主内容区域 -->
    <div class="layout__container">
      <!-- 全局头部导航组件：仅在非隐藏侧边栏的页面（如登录页）显示 -->
      <HeaderNav v-if="!hideSidebar" />

      <!-- 主内容区域 -->
      <main
        class="layout__main"
        :class="{ 'layout__main--login': hideSidebar }"
      >
        <!-- 路由出口 -->
        <router-view />
      </main>
    </div>

    <!-- 锁屏组件 -->
    <LockScreen />

    <!-- 侧边栏遮罩层：移动端使用 -->
    <div
      class="layout__sidebar-overlay"
      v-if="!ui.sidebarHidden && !hideSidebar"
      @click="ui.hideSidebar()"
    />
  </div>
</template>

<script setup lang="ts">
// 引入头部导航组件
import HeaderNav from "./components/HeaderNav.vue";
// 引入侧边栏组件
import Sidebar from "./components/Sidebar.vue";
// 引入锁屏组件
import LockScreen from "./components/LockScreen.vue";
// 引入全局 UI Store，用于管理侧边栏显示状态
import { useUIStore } from "./stores/ui";
// 引入路由钩子以获取当前路由对象
import { useRoute } from "vue-router";
// 引入 Vue 的计算属性工具
import { computed } from "vue";
// 初始化 UI Store 实例
const ui = useUIStore();
// 获取当前激活的路由对象
const route = useRoute();
// 计算属性：根据路由元信息决定是否隐藏侧边栏（登录/注册页等）
const hideSidebar = computed(
  () => !!(route.meta && (route.meta as any).hideSidebar)
);
</script>

<style>
* {
  box-sizing: border-box;
}
:root {
  /* 应用背景色（浅蓝） */
  --bg: #f0f9ff;
  /* 表面色（白色，卡片/主内容背景） */
  --surface: #ffffff;
  /* 主文本颜色（深）*/
  --text-primary: #0f172a;
  /* 次级文本颜色（灰色） */
  --text-muted: #64748b;
  /* 边框颜色（浅灰） */
  --border: #e2e8f0;
  /* 主品牌色（蓝色） */
  --accent: #0ea5e9;
  /* 品牌色悬停态 */
  --accent-hover: #0284c7;
  /* 活跃态背景色（浅蓝） */
  --active: #e0f2fe;
  /* 悬停态背景色（更浅的灰蓝） */
  --hover: #f1f5f9;
  /* 头部背景色 */
  --header-bg: #e0f2fe;
  /* 头部高度变量 */
  --header-h: 56px;
}
/* 全局 body 样式：字体、背景与文本颜色 */
body {
  margin: 0;
  padding: 0;
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial,
    "Noto Sans", "Apple Color Emoji", "Segoe UI Emoji";
  background: var(--bg);
  color: var(--text-primary);
  width: 100%;
  overflow-x: hidden;
}
html {
  margin: 0;
  padding: 0;
  width: 100%;
}
/* 根布局容器：水平排列侧边栏与右侧区域 */
.layout {
  display: flex;
  flex-direction: row;
  height: 100vh;
  width: 100%;
  overflow: hidden;
}
/* 右侧容器：垂直排列头部与主内容 */
.layout__container {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
  background: var(--bg);
  height: 100%;
}
/* 主内容区域：可滚动，卡片背景色 */
.layout__main {
  flex: 1;
  overflow: auto;
  padding: 16px;
  background: var(--surface);
  width: 100%;
}
/* 登录态主区：使用渐变背景，限制滚动以适配登录页视觉 */
.layout__main--login {
  background: linear-gradient(180deg, #f0f9ff 0%, #ffffff 40%, #f8fafc 100%);
  min-height: 100vh;
  width: 100%;
  overflow-x: hidden;
  overflow-y: auto;
  padding: 0;
  display: flex;
  flex-direction: column;
}
/* 头部布局：左右分布、底部分隔线与固定高度 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--header-bg);
  min-height: var(--header-h);
  width: 100%;
}
/* 头部左侧：Logo 与导航的容器 */
.header__left {
  display: flex;
  align-items: center;
  gap: 16px;
}
/* Logo 文案样式已删除 */
/* 头部导航容器：横向排列 */
.header__nav {
  display: flex;
  gap: 12px;
}
/* 导航项基础样式：内边距与圆角 */
.header__nav-item {
  padding: 8px 12px;
  border-radius: 6px;
}
/* 导航项悬停态：浅色背景 */
.header__nav-item:hover {
  background: var(--hover);
}
/* 导航项选中态：高亮背景 */
.header__nav-item--active {
  background: var(--active);
}
/* 头部右侧：搜索、用户菜单等容器 */
.header__right {
  display: flex;
  align-items: center;
  gap: 12px;
}
/* 搜索容器：相对定位以放置搜索图标 */
.header__search {
  position: relative;
}
/* 搜索输入框：内边距、边框、圆角与颜色 */
.header__search-input {
  padding: 8px 28px 8px 10px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--surface);
  color: var(--text-primary);
}
/* 搜索输入聚焦态：品牌色边框与轻量阴影 */
.header__search-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.2);
}
/* 搜索图标：绝对定位居右垂直居中，次级文本色 */
.header__search-icon {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}
/* 页面通用区块：纵向排列并设置间距 */
.layout__section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
/* 页面头部：左右分布与底部间距 */
.layout__page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
/* 页面标题：字号与加粗 */
.layout__page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}
/* 页面副标题：较小字号与次级色 */
.layout__page-subtitle {
  font-size: 13px;
  color: var(--text-muted);
}
/* 卡片容器：背景、边框、圆角与阴影 */
.layout__card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: 0 6px 24px rgba(16, 24, 40, 0.08);
}
/* 卡片头部：内边距与底部分隔线 */
.layout__card-header {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
}
/* 卡片标题：字号与加粗 */
.layout__card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}
/* 卡片主体：统一内边距 */
.layout__card-body {
  padding: 12px 16px;
}
/* 按钮基础样式：内边距、边框、圆角与颜色 */
.btn {
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--surface);
  color: var(--text-primary);
}
/* 主按钮：品牌色背景与白色文字 */
.btn--primary {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}
/* 主按钮悬停态：更深的品牌色 */
.btn--primary:hover {
  background: var(--accent-hover);
  border-color: var(--accent-hover);
}
/* 按钮悬停态：浅色背景 */
.btn:hover {
  background: var(--hover);
}
/* 按钮聚焦态：可访问性高亮阴影 */
.btn:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.2);
}
/* 按钮禁用态：降低透明度与禁用指针 */
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
/* 主按钮禁用态：同样降低透明度与禁用指针 */
.btn--primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
/* 通用工具类：隐藏元素 */
.u-hidden {
  display: none;
}
.u-hidden-mobile {
  display: flex;
}
.u-hidden-mobile-up {
  display: none;
}
@media (max-width: 768px) {
  .u-hidden-mobile {
    display: none !important;
  }
  .u-hidden-mobile-up {
    display: flex !important;
  }
}
/* 仪表盘表格：宽度满、合并边框 */
.dashboard__table {
  width: 100%;
  border-collapse: collapse;
}
/* 表格单元格：底部分隔线与内边距，左对齐 */
.dashboard__table th,
.dashboard__table td {
  border-bottom: 1px solid var(--border);
  padding: 8px 10px;
  text-align: left;
}
/* 表头背景：活跃态色 */
.dashboard__table-head {
  background: var(--active);
}
/* 表头文本：加粗与主文本色 */
.dashboard__table-th {
  font-weight: 600;
  color: var(--text-primary);
}
/* 行悬停态：浅色背景高亮 */
.dashboard__table-row:hover {
  background: var(--hover);
}
/* 工具类：更小的文字 */
.u-text-sm {
  font-size: 12px;
}
/* 工具类：中等字体粗细 */
.u-font-medium {
  font-weight: 600;
}
/* 工具类：文本颜色（使用主文本色） */
.u-text-gray-700 {
  color: var(--text-primary);
}
/* 工具类：无内边距 */
.u-p-0 {
  padding: 0;
}
/* 工具类：横向滚动容器 */
.u-overflow-x-auto {
  overflow-x: auto;
}
/* 工具类：左外边距 4px */
.u-ml-1 {
  margin-left: 4px;
}
/* 工具类：左外边距 8px */
.u-ml-2 {
  margin-left: 8px;
}
/* 工具类：左外边距 12px */
.u-ml-3 {
  margin-left: 12px;
}
/* 工具类：右外边距 8px */
.u-mr-2 {
  margin-right: 8px;
}

/* 文本选中态：品牌色背景与白色文字 */
::selection {
  background: var(--accent);
  color: #fff;
}

/* 响应式：窄屏适配（最大宽度 768px） */
@media (max-width: 768px) {
  /* 移动端隐藏头部搜索框以节省空间 */
  .header__search {
    display: none;
  }
  .header {
    padding: 8px 12px;
    gap: 8px;
  }
  .header__logo {
    font-size: 18px;
  }
  .header__right {
    gap: 8px;
  }
  /* 移动端主区内边距稍减 */
  .layout__main {
    padding: 12px;
  }
  /* 侧边栏改为抽屉式固定定位并增加阴影 */
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    width: 280px;
    z-index: 2000;
    box-shadow: 12px 0 32px rgba(0, 0, 0, 0.25);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }
  /* 遮罩层优化 */
  .layout__sidebar-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(2px);
    z-index: 1999;
    animation: fadeIn 0.3s ease;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
