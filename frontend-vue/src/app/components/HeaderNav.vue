<template>
  <header class="header" role="banner">
    <div class="header__left">
      <h1 class="header__logo">ClusterManager</h1>
      <nav class="header__nav" role="navigation" aria-label="主导航">
        <RouterLink class="header__nav-item" :class="{ 'header__nav-item--active': isActive('/cluster-list') }" to="/cluster-list">集群列表</RouterLink>
        <RouterLink class="header__nav-item" :class="{ 'header__nav-item--active': isActive('/logs') }" to="/logs">日志查询</RouterLink>
        <RouterLink v-if="can(['admin','operator'])" class="header__nav-item" :class="{ 'header__nav-item--active': isActive('/diagnosis') }" to="/diagnosis">故障诊断</RouterLink>
        <RouterLink class="header__nav-item" :class="{ 'header__nav-item--active': isActive('/fault-center') }" to="/fault-center">故障中心</RouterLink>
        <RouterLink class="header__nav-item" :class="{ 'header__nav-item--active': isActive('/exec-logs') }" to="/exec-logs">执行日志</RouterLink>
        <div class="header__dropdown" v-if="can(['admin','operator'])">
          <button class="header__nav-item">系统配置 <i class="fas fa-chevron-down"></i></button>
          <div class="header__dropdown-menu">
            <RouterLink class="header__dropdown-item" to="/alert-config">告警配置</RouterLink>
          </div>
        </div>
      </nav>
    </div>
    <div class="header__right">
      <div class="header__search">
        <input id="global-search" class="header__search-input" placeholder="搜索节点、日志或配置..." />
        <i class="fas fa-search header__search-icon"></i>
      </div>
      <div class="header__user-menu" v-if="authed">
        <button class="header__user-avatar"><i class="fas fa-user"></i></button>
        <div class="header__user-dropdown">
          <RouterLink class="header__user-dropdown-item" to="/profile">个人主页</RouterLink>
          <RouterLink class="header__user-dropdown-item" to="/account">账号管理</RouterLink>
          <a class="header__user-dropdown-item" href="#" @click.prevent="onLogout">退出登录</a>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '../stores/auth'
const route = useRoute()
const auth = useAuthStore()
auth.restore()
const authed = auth.isAuthenticated
function isActive(p: string) { return route.path === p }
function can(roles: string[]) { return roles.includes(auth.role || '') }
function onLogout() { auth.logout() }
</script>

