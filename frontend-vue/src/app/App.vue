<template>
  <div class="layout">
    <HeaderNav />
    <div class="layout__container">
      <Sidebar v-show="!ui.sidebarHidden" />
      <main class="layout__main">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import HeaderNav from './components/HeaderNav.vue'
import Sidebar from './components/Sidebar.vue'
import { useUIStore } from './stores/ui'
const ui = useUIStore()
</script>

<style>
body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Noto Sans", "Apple Color Emoji", "Segoe UI Emoji" }
.layout { display: flex; flex-direction: column; height: 100vh }
.layout__container { display: flex; flex: 1; min-height: 0 }
.layout__main { flex: 1; overflow: auto; padding: 16px }
.header { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; border-bottom: 1px solid #e5e7eb }
.header__left { display: flex; align-items: center; gap: 16px }
.header__logo { font-family: Pacifico, cursive; font-size: 20px }
.header__nav { display: flex; gap: 12px }
.header__nav-item { padding: 8px 12px; border-radius: 6px }
.header__nav-item--active { background: #eef2ff }
.header__right { display: flex; align-items: center; gap: 12px }
.header__search { position: relative }
.header__search-input { padding: 8px 28px 8px 10px; border: 1px solid #e5e7eb; border-radius: 6px }
.header__search-icon { position: absolute; right: 8px; top: 50%; transform: translateY(-50%); color: #6b7280 }
.sidebar { width: 240px; border-right: 1px solid #e5e7eb; padding: 12px; overflow: auto }
.sidebar__nav { display: flex; flex-direction: column; gap: 8px }
.sidebar__link { padding: 8px 10px; border-radius: 6px }
.sidebar__link--active { background: #f1f5f9 }
.btn { padding: 8px 12px; border: 1px solid #e5e7eb; border-radius: 6px }
.u-hidden { display: none }
.dashboard__table { width: 100%; border-collapse: collapse }
.dashboard__table th, .dashboard__table td { border-bottom: 1px solid #e5e7eb; padding: 8px 10px; text-align: left }
.dashboard__table-row:hover { background: #f8fafc }
.u-text-sm { font-size: 12px }
.u-font-medium { font-weight: 600 }
.u-text-gray-700 { color: #374151 }
.u-ml-1 { margin-left: 4px }
.u-ml-2 { margin-left: 8px }
.u-ml-3 { margin-left: 12px }
</style>
