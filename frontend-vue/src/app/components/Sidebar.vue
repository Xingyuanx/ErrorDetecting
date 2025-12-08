<template>
  <aside class="sidebar" role="complementary" aria-label="权限管理导航">
    <nav class="sidebar__nav" role="navigation" aria-label="权限管理">
      <RouterLink v-if="isAdmin" class="sidebar__link" :class="{ 'sidebar__link--active': isActive('/user-management') }" to="/user-management">用户管理</RouterLink>
      <RouterLink v-if="isAdmin" class="sidebar__link" :class="{ 'sidebar__link--active': isActive('/role-assignment') }" to="/role-assignment">角色分配</RouterLink>
      <RouterLink v-if="isAdmin" class="sidebar__link" :class="{ 'sidebar__link--active': isActive('/permission-policy') }" to="/permission-policy">权限策略</RouterLink>
      <RouterLink v-if="isAdmin" class="sidebar__link" :class="{ 'sidebar__link--active': isActive('/audit-logs') }" to="/audit-logs">审计日志</RouterLink>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { useRoute, RouterLink } from 'vue-router'
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '../stores/auth'
const route = useRoute()
const auth = useAuthStore()
const { role } = storeToRefs(auth)
function isActive(p: string) { return route.path === p }
const isAdmin = computed(() => role.value === 'admin')
</script>
