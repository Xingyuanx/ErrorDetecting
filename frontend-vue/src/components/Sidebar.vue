<template>
  <el-menu
    :default-active="route.path"
    class="sidebar-menu"
    :collapse="ui.sidebarHidden"
    :collapse-transition="false"
    router
  >
    <div class="logo-container" :class="{ 'is-collapse': ui.sidebarHidden }">
      <el-icon :size="24" color="#0ea5e9"><Monitor /></el-icon>
      <span v-if="!ui.sidebarHidden" class="logo-text">ClusterManager</span>
    </div>

    <el-menu-item v-if="can([Roles.admin, Roles.operator])" index="/diagnosis">
      <el-icon><Search /></el-icon>
      <template #title>故障诊断</template>
    </el-menu-item>

    <el-menu-item index="/cluster-list">
      <el-icon><Grid /></el-icon>
      <template #title>集群列表</template>
    </el-menu-item>

    <el-menu-item index="/logs">
      <el-icon><Document /></el-icon>
      <template #title>集群日志</template>
    </el-menu-item>

    <el-menu-item index="/hadoop-exec-logs">
      <el-icon><Operation /></el-icon>
      <template #title>集群操作日志</template>
    </el-menu-item>

    <el-sub-menu v-if="can([Roles.admin, Roles.operator])" index="auth-control">
      <template #title>
        <el-icon><Lock /></el-icon>
        <span>角色权限控制</span>
      </template>
      <el-menu-item v-if="can([Roles.admin])" index="/user-management">
        <el-icon><User /></el-icon>
        <template #title>用户管理</template>
      </el-menu-item>
      <el-menu-item v-if="can([Roles.admin])" index="/operation-logs">
        <el-icon><Clock /></el-icon>
        <template #title>系统操作日志</template>
      </el-menu-item>
    </el-sub-menu>
  </el-menu>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import { storeToRefs } from "pinia";
import { useAuthStore } from "../stores/auth";
import { useUIStore } from "../stores/ui";
import { Roles } from "../constants/roles";
import {
  Monitor,
  Search,
  Grid,
  Document,
  Operation,
  Lock,
  User,
  Clock,
} from "@element-plus/icons-vue";

const route = useRoute();
const auth = useAuthStore();
const ui = useUIStore();
const { role } = storeToRefs(auth);

function can(roles: string[]) {
  return roles.includes(role.value || "");
}
</script>

<style scoped>
.sidebar-menu {
  border-right: 1px solid rgba(0, 0, 0, 0.2);
  height: 100%;
  width: 100% !important;
  background-color: var(--app-sidebar-bg);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 4px 0 10px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

/* 隐藏收起时的文字，防止闪烁 */
:deep(.el-menu--collapse) .el-sub-menu__title span,
:deep(.el-menu--collapse) .el-menu-item span,
:deep(.el-menu--collapse) .el-sub-menu__icon-arrow {
  display: none;
}

/* 确保所有层级的菜单背景统一 */
.sidebar-menu,
:deep(.el-menu),
:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  background-color: var(--app-sidebar-bg) !important;
}

:global(html.dark) .sidebar-menu {
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: none;
}

.logo-container {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 12px;
  background-color: var(--app-sidebar-bg);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  white-space: nowrap;
}

.logo-container.is-collapse {
  padding: 0 20px;
  justify-content: center;
}

.logo-text {
  color: var(--app-sidebar-text-active);
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
}

:deep(.el-menu-item.is-active) {
  background-color: var(--el-color-primary) !important;
  color: #ffffff !important;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
}

:deep(.el-menu-item.is-active .el-icon) {
  color: #ffffff !important;
}

:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  color: var(--app-sidebar-text);
}

:deep(.el-menu-item .el-icon),
:deep(.el-sub-menu__title .el-icon) {
  color: var(--app-sidebar-text);
}

:deep(.el-menu-item:hover),
:deep(.el-sub-menu__title:hover) {
  background-color: var(--app-sidebar-item-hover) !important;
  color: var(--app-sidebar-text-active) !important;
}

:deep(.el-menu-item:hover .el-icon),
:deep(.el-sub-menu__title:hover .el-icon) {
  color: var(--app-sidebar-text-active) !important;
}

:deep(.el-sub-menu__icon-arrow) {
  color: var(--app-sidebar-text);
}

:deep(.el-sub-menu:hover .el-sub-menu__icon-arrow) {
  color: var(--app-sidebar-text-active) !important;
}
</style>
