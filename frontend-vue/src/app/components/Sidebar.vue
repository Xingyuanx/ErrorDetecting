<template>
  <el-menu
    :default-active="route.path"
    class="sidebar-menu"
    :collapse="ui.sidebarHidden"
    background-color="#001529"
    text-color="rgba(255, 255, 255, 0.65)"
    active-text-color="#fff"
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
import { Monitor, Search, Grid, Document, Operation, Lock, User, Clock } from '@element-plus/icons-vue'

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
  border-right: none;
  height: 100%;
}

.logo-container {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 12px;
  background-color: #002140;
  transition: all 0.3s;
  overflow: hidden;
}

.logo-container.is-collapse {
  padding: 0 20px;
  justify-content: center;
}

.logo-text {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
}

:deep(.el-menu-item.is-active) {
  background-color: var(--el-color-primary) !important;
}

:deep(.el-menu-item:hover) {
  color: #fff !important;
}
</style>
