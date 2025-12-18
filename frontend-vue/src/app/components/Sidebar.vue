<template>
  <aside class="sidebar" role="complementary" aria-label="侧边栏">
    <nav class="sidebar__nav" role="navigation" aria-label="主导航">
      <RouterLink class="sidebar__link" :class="{ 'sidebar__link--active': isActive('/cluster-list') }" to="/cluster-list">集群列表</RouterLink>
      <RouterLink class="sidebar__link" :class="{ 'sidebar__link--active': isActive('/logs') }" to="/logs">日志查询</RouterLink>
      <RouterLink class="sidebar__link" :class="{ 'sidebar__link--active': isActive('/exec-logs') }" to="/exec-logs">执行日志</RouterLink>
      <RouterLink v-if="can([Roles.admin, Roles.operator])" class="sidebar__link" :class="{ 'sidebar__link--active': isActive('/diagnosis') }" to="/diagnosis">故障诊断</RouterLink>
    </nav>
    <div class="sidebar__dropdown" v-if="can([Roles.admin, Roles.operator])">
      <button class="sidebar__link sidebar__dropdown-trigger" type="button" aria-haspopup="true" :aria-expanded="configOpen ? 'true' : 'false'" @click.stop.prevent="toggleConfig">
        系统配置
        <i class="fas fa-chevron-down sidebar__dropdown-icon" :class="{ 'icon-rot': configOpen }" aria-hidden="true"></i>
      </button>
      <div class="sidebar__dropdown-menu" :class="{ 'sidebar__dropdown-menu--show': configOpen }" role="menu">
        <RouterLink class="sidebar__dropdown-item" to="/alert-config" role="menuitem" @click.stop="closeAll">告警配置</RouterLink>
      </div>
    </div>
    <div class="sidebar__dropdown" v-if="can([Roles.admin, Roles.operator])">
      <button class="sidebar__link sidebar__dropdown-trigger" type="button" aria-haspopup="true" :aria-expanded="permOpen ? 'true' : 'false'" @click.stop.prevent="togglePerm">
        角色权限控制
        <i class="fas fa-chevron-down sidebar__dropdown-icon" :class="{ 'icon-rot': permOpen }" aria-hidden="true"></i>
      </button>
      <div class="sidebar__dropdown-menu" :class="{ 'sidebar__dropdown-menu--show': permOpen }" role="menu">
        <RouterLink v-if="can([Roles.admin])" class="sidebar__dropdown-item" to="/user-management" role="menuitem" @click.stop="closeAll">用户管理</RouterLink>
        <RouterLink v-if="can([Roles.admin])" class="sidebar__dropdown-item" to="/audit-logs" role="menuitem" @click.stop="closeAll">审计日志</RouterLink>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '../stores/auth'
import { Roles } from '../constants/roles'
const route = useRoute()
const auth = useAuthStore()
const { role } = storeToRefs(auth)
function isActive(p: string) { return route.path === p }
function can(roles: string[]) { return roles.includes(role.value || '') }
const configOpen = ref(false)
const permOpen = ref(false)
function toggleConfig(){ const next = !configOpen.value; closeAll(); configOpen.value = next }
function togglePerm(){ const next = !permOpen.value; closeAll(); permOpen.value = next }
function closeAll(){ configOpen.value = false; permOpen.value = false }
function onDocClick(){ closeAll() }
onMounted(()=>{ document.addEventListener('click', onDocClick) })
onUnmounted(()=>{ document.removeEventListener('click', onDocClick) })
</script>

<style scoped>
.sidebar__section-title{ color:#6b7280; font-size:13px; font-weight:600; margin:12px 0 8px }
.sidebar__dropdown{ position: relative; margin-top: 12px }
.sidebar__dropdown-trigger{ display:flex; align-items:center; justify-content:space-between; gap:6px; width:100% }
.sidebar__dropdown-icon{ font-size:12px; transition: transform 120ms ease }
.icon-rot{ transform: rotate(180deg) }
.sidebar__dropdown-menu{ position:absolute; top:100%; left:0; margin-top:4px; width:12rem; max-width:calc(100% - 8px); background:#fff; border-radius:8px; box-shadow:0 12px 32px rgba(16,24,40,0.12); padding:4px 0; opacity:0; visibility:hidden; transform: translateY(-8px); transition: all 120ms ease; z-index: 10 }
.sidebar__dropdown-menu--show{ opacity:1; visibility:visible; transform: translateY(0) }
.sidebar__dropdown-item{ display:block; padding:8px 12px; border-radius:6px }
.sidebar__dropdown-item:hover{ background:#f3f4f6 }
</style>
