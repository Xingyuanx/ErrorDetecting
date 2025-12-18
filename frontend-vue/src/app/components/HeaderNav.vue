<template>
  <header class="header" role="banner">
    <div class="header__left">
      <h1 class="header__logo">ClusterManager</h1>
      <nav class="header__nav" role="navigation" aria-label="主导航"></nav>
    </div>
  <div class="header__right">
    <div v-if="!hideSidebar" class="header__search">
      <input id="global-search" class="header__search-input" placeholder="搜索节点、日志或配置..." />
      <i class="fas fa-search header__search-icon"></i>
    </div>
    <button v-if="!hideSidebar" class="btn u-ml-3" type="button" @click="toggleSidebar">{{ ui.sidebarHidden ? '显示侧边栏' : '隐藏侧边栏' }}</button>
    <div class="header__user-menu" v-if="authed">
      <button class="header__user-avatar" type="button">
        <i class="fas fa-user"></i>
      </button>
      <div class="header__user-dropdown" role="menu">
          <RouterLink class="header__user-dropdown-item" to="/profile" role="menuitem">个人主页</RouterLink>
          <RouterLink class="header__user-dropdown-item" to="/account" role="menuitem">账号管理</RouterLink>
          <a class="header__user-dropdown-item" href="#" role="menuitem" @click.prevent="onLogout">退出登录</a>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { RouterLink } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '../stores/auth'
import { useUIStore } from '../stores/ui'
import { Roles } from '../constants/roles'
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const { isAuthenticated, role } = storeToRefs(auth)
function isActive(p: string) { return route.path === p }
const authed = isAuthenticated
function can(roles: string[]) { return roles.includes(role.value || '') }
function onLogout() { auth.logout(); router.replace({ name: 'login' }) }
const ui = useUIStore()
function toggleSidebar(){ ui.toggleSidebar() }
const hideSidebar = computed(() => !!(route.meta && (route.meta as any).hideSidebar))
function onDocClick(){ closeAll() }
onMounted(()=>{ document.addEventListener('click', onDocClick) })
onUnmounted(()=>{ document.removeEventListener('click', onDocClick) })
function closeAll(){}
</script>

<style scoped>
.header__dropdown{ position: relative }
.header__dropdown-trigger{ display:flex; align-items:center; gap:6px }
.header__dropdown-icon{ font-size:12px; transition: transform 120ms ease }
.icon-rot{ transform: rotate(180deg) }
.header__dropdown-menu{ position:absolute; top:100%; left:0; margin-top:4px; width:12rem; background:#fff; border-radius:8px; box-shadow:0 12px 32px rgba(16,24,40,0.12); padding:4px 0; opacity:0; visibility:hidden; transform: translateY(-8px); transition: all 120ms ease }
.header__dropdown-menu--show{ opacity:1; visibility:visible; transform: translateY(0) }
.header__dropdown-item{ display:block; padding:8px 12px; border-radius:6px }
.header__dropdown-item:hover{ background:#f3f4f6 }

.header__user-menu{ position: relative }
.header__user-avatar{ width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; border:1px solid #e5e7eb; background:#fff }
.header__user-dropdown{ position:absolute; top:100%; right:0; margin-top:4px; width:12rem; background:#fff; border-radius:8px; box-shadow:0 12px 32px rgba(16,24,40,0.12); padding:4px 0; opacity:0; visibility:hidden; transform: translateY(-8px); transition: all 120ms ease }
.header__user-menu:hover .header__user-dropdown{ opacity:1; visibility:visible; transform: translateY(0) }
.header__user-dropdown-item{ display:block; padding:8px 12px; border-radius:6px }
.header__user-dropdown-item:hover{ background:#f3f4f6 }
</style>
