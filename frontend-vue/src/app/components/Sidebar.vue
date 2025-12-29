<template>
  <aside
    class="sidebar"
    :class="{ 'is-collapse': ui.sidebarHidden }"
    role="complementary"
    aria-label="侧边栏"
  >
    <nav class="sidebar__nav" role="navigation" aria-label="主导航">
      <!-- 基础导航项 -->
      <div class="sidebar__mobile-header u-hidden-mobile-up">
        <span class="sidebar__mobile-logo">
          <i class="fas fa-microchip u-mr-2"></i>
          <span class="sidebar__text">ClusterManager</span>
        </span>
      </div>
      <RouterLink
        class="sidebar__item"
        to="/cluster-list"
        :class="{ 'is-active': isActive('/cluster-list') }"
        title="集群列表"
      >
        <i class="fas fa-th-list sidebar__icon"></i>
        <span class="sidebar__text">集群列表</span>
      </RouterLink>

      <RouterLink
        class="sidebar__item"
        to="/logs"
        :class="{ 'is-active': isActive('/logs') }"
        title="故障日志"
      >
        <i class="fas fa-clipboard-list sidebar__icon"></i>
        <span class="sidebar__text">故障日志</span>
      </RouterLink>

      <RouterLink
        class="sidebar__item"
        to="/exec-logs"
        :class="{ 'is-active': isActive('/exec-logs') }"
        title="执行日志"
      >
        <i class="fas fa-terminal sidebar__icon"></i>
        <span class="sidebar__text">执行日志</span>
      </RouterLink>

      <RouterLink
        v-if="can([Roles.admin, Roles.operator])"
        class="sidebar__item"
        to="/diagnosis"
        :class="{ 'is-active': isActive('/diagnosis') }"
        title="故障诊断"
      >
        <i class="fas fa-microscope sidebar__icon"></i>
        <span class="sidebar__text">故障诊断</span>
      </RouterLink>

      <!-- 系统配置 (子菜单) -->
      <div
        v-if="can([Roles.admin, Roles.operator])"
        class="sidebar__sub-menu"
        :class="{ 'is-opened': isOpened('1') && !ui.sidebarHidden }"
      >
        <div
          class="sidebar__sub-menu-title"
          @click="toggleMenu('1')"
          title="系统配置"
        >
          <i class="fas fa-sliders-h sidebar__icon"></i>
          <span class="sidebar__text">系统配置</span>
          <i
            v-if="!ui.sidebarHidden"
            class="fas fa-chevron-down sidebar__arrow"
            :class="{ 'is-rotated': isOpened('1') }"
          ></i>
        </div>
        <div class="sidebar__sub-menu-content">
          <RouterLink
            class="sidebar__item sidebar__item--sub"
            to="/alert-config"
            :class="{ 'is-active': isActive('/alert-config') }"
            title="告警配置"
          >
            <i class="fas fa-bell sidebar__icon"></i>
            <span class="sidebar__text">告警配置</span>
          </RouterLink>
        </div>
      </div>

      <!-- 角色权限控制 (子菜单) -->
      <div
        v-if="can([Roles.admin, Roles.operator])"
        class="sidebar__sub-menu"
        :class="{ 'is-opened': isOpened('2') && !ui.sidebarHidden }"
      >
        <div
          class="sidebar__sub-menu-title"
          @click="toggleMenu('2')"
          title="角色权限控制"
        >
          <i class="fas fa-user-shield sidebar__icon"></i>
          <span class="sidebar__text">角色权限控制</span>
          <i
            v-if="!ui.sidebarHidden"
            class="fas fa-chevron-down sidebar__arrow"
            :class="{ 'is-rotated': isOpened('2') }"
          ></i>
        </div>
        <div class="sidebar__sub-menu-content">
          <RouterLink
            v-if="can([Roles.admin])"
            class="sidebar__item sidebar__item--sub"
            to="/user-management"
            :class="{ 'is-active': isActive('/user-management') }"
            title="用户管理"
          >
            <i class="fas fa-users sidebar__icon"></i>
            <span class="sidebar__text">用户管理</span>
          </RouterLink>
          <RouterLink
            v-if="can([Roles.admin])"
            class="sidebar__item sidebar__item--sub"
            to="/audit-logs"
            :class="{ 'is-active': isActive('/audit-logs') }"
            title="操作日志"
          >
            <i class="fas fa-history sidebar__icon"></i>
            <span class="sidebar__text">操作日志</span>
          </RouterLink>
        </div>
      </div>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute, RouterLink } from "vue-router";
import { storeToRefs } from "pinia";
import { useAuthStore } from "../stores/auth";
import { useUIStore } from "../stores/ui";
import { Roles } from "../constants/roles";

const route = useRoute();
const auth = useAuthStore();
const ui = useUIStore();
const { role } = storeToRefs(auth);

// 判断当前路径是否激活
function isActive(p: string) {
  return route.path === p;
}

// 权限校验
function can(roles: string[]) {
  return roles.includes(role.value || "");
}

// 下拉菜单状态管理
const openedMenus = ref<string[]>([]);

// 判断菜单是否展开
function isOpened(index: string) {
  return openedMenus.value.includes(index);
}

// 切换菜单展开/收起
function toggleMenu(index: string) {
  // 如果侧边栏是收起状态，点击子菜单标题时不展开（或者你可以实现弹出菜单）
  if (ui.sidebarHidden) return;

  const i = openedMenus.value.indexOf(index);
  if (i > -1) {
    openedMenus.value.splice(i, 1);
  } else {
    openedMenus.value.push(index);
  }
}
</script>

<style scoped>
/* 侧边栏基础样式 */
.sidebar {
  width: 240px;
  background: var(--surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  transition: width 0.3s, transform 0.3s;
  overflow-x: hidden;
  overflow-y: auto;
  flex-shrink: 0;
}

/* 折叠状态样式 */
.sidebar.is-collapse {
  width: 64px;
  overflow: visible;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .sidebar.is-collapse {
    width: 280px; /* 移动端展开时保持固定宽度 */
    transform: translateX(-100%);
    box-shadow: none;
  }
  .sidebar:not(.is-collapse) {
    transform: translateX(0);
  }
}

.sidebar__nav {
  padding: 12px 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* 菜单项基础样式 */
.sidebar__item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: var(--text-primary);
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
  gap: 12px;
  white-space: nowrap;
}

.sidebar__item:hover {
  background-color: var(--hover);
  color: var(--accent);
}

.sidebar__item.is-active {
  color: var(--accent);
  background-color: var(--active);
  font-weight: 600;
}

/* 折叠时文字隐藏 */
.is-collapse .sidebar__text {
  display: none;
}

/* 图标样式 */
.sidebar__icon {
  width: 24px; /* 固定宽度保证对齐 */
  min-width: 24px;
  text-align: center;
  font-size: 18px;
  color: var(--text-muted);
}

.is-active .sidebar__icon {
  color: var(--accent);
}

/* 子菜单容器 */
.sidebar__sub-menu {
  display: flex;
  flex-direction: column;
}

/* 子菜单标题 */
.sidebar__sub-menu-title {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
  gap: 12px;
  white-space: nowrap;
}

.sidebar__sub-menu-title:hover {
  background-color: var(--hover);
}

/* 箭头旋转动画 */
.sidebar__arrow {
  margin-left: auto;
  font-size: 12px;
  transition: transform 0.3s;
  color: var(--text-muted);
}

.sidebar__arrow.is-rotated {
  transform: rotate(180deg);
}

/* 子菜单内容 (手风琴效果) */
.sidebar__sub-menu-content {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease-out;
  background-color: rgba(0, 0, 0, 0.02);
}

.is-opened .sidebar__sub-menu-content {
  max-height: 200px;
}

/* 侧边栏收起时的弹出菜单 (Popup) 逻辑 */
.sidebar__mobile-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 8px;
}

.sidebar__mobile-logo {
  display: flex;
  align-items: center;
  font-family: Pacifico, cursive;
  font-size: 18px;
  color: var(--accent);
  transition: all 0.3s;
}

.is-collapse .sidebar__mobile-header {
  padding: 16px 0;
  justify-content: center;
}

.is-collapse .sidebar__mobile-logo .u-mr-2 {
  margin-right: 0;
}

/* --- 侧边栏收起时的弹出菜单 (Popup) 逻辑 --- */

/* 收起状态下，子菜单容器设为相对定位 */
.is-collapse .sidebar__sub-menu {
  position: relative;
}

/* 悬停时显示弹出菜单 */
.is-collapse .sidebar__sub-menu:hover .sidebar__sub-menu-content {
  max-height: none;
  overflow: visible;
  position: absolute;
  left: 100%; /* 紧贴侧边栏右侧 */
  top: 0;
  width: 180px;
  background-color: var(--surface);
  border: 1px solid var(--border);
  border-left: none;
  box-shadow: 6px 0 16px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  padding: 4px 0;
  border-radius: 0 4px 4px 0;
}

/* 弹出菜单中的项样式 */
.is-collapse .sidebar__sub-menu:hover .sidebar__item--sub {
  padding: 12px 16px;
  width: 100%;
}

.is-collapse .sidebar__sub-menu:hover .sidebar__item--sub .sidebar__text {
  display: inline; /* 强制显示文字 */
  color: var(--text-primary);
}

.is-collapse .sidebar__sub-menu:hover .sidebar__item--sub:hover {
  background-color: var(--hover);
}

/* 子菜单项缩进 */
.sidebar__item--sub {
  padding-left: 56px;
}
</style>
