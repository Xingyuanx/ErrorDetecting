<template>
  <el-config-provider>
    <div class="layout-wrapper">
      <el-container v-if="!hideSidebar" class="main-container">
        <!-- 移动端遮罩层 -->
        <transition name="fade">
          <div 
            v-if="isMobile && !ui.sidebarHidden" 
            class="mobile-mask" 
            @click="ui.hideSidebar()"
          ></div>
        </transition>
        <el-aside 
          :width="ui.sidebarHidden ? '64px' : '220px'" 
          class="aside-menu"
          :class="{ 'is-mobile-hidden': isMobile && ui.sidebarHidden, 'is-mobile-show': isMobile && !ui.sidebarHidden }"
        >
          <Sidebar />
        </el-aside>
        <el-container class="content-container">
          <el-header height="56px" class="header-nav">
            <HeaderNav />
          </el-header>
          <el-main class="main-content">
            <router-view />
          </el-main>
        </el-container>
      </el-container>

      <div v-else class="login-layout">
        <router-view />
      </div>

      <LockScreen />
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { ElConfigProvider } from 'element-plus'
import HeaderNav from "./components/HeaderNav.vue";
import Sidebar from "./components/Sidebar.vue";
import LockScreen from "./components/LockScreen.vue";
import { useUIStore } from "./stores/ui";
import { useRoute } from "vue-router";
import { computed, ref, onMounted, onUnmounted, watch } from "vue";

const ui = useUIStore();
const route = useRoute();

// 路由切换时，如果是移动端则自动收起侧边栏
watch(() => route.path, () => {
  if (isMobile.value && !ui.sidebarHidden) {
    ui.hideSidebar();
  }
});

const hideSidebar = computed(
  () => !!(route.meta && (route.meta as any).hideSidebar)
);

const isMobile = ref(window.innerWidth < 768);
const updateWidth = () => {
  isMobile.value = window.innerWidth < 768;
  if (isMobile.value && !ui.sidebarHidden) {
    ui.hideSidebar();
  }
};

onMounted(() => {
  window.addEventListener('resize', updateWidth);
  updateWidth();
});

onUnmounted(() => {
  window.removeEventListener('resize', updateWidth);
});
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: var(--el-font-family);
  background-color: var(--app-bg);
  color: var(--app-text-primary);
  transition: background-color 0.3s, color 0.3s;
}

#app {
  height: 100%;
}

.layout-wrapper {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.main-container {
  height: 100%;
}

.aside-menu {
  background-color: var(--app-header-bg);
  border-right: 1px solid var(--app-border-color);
  transition: width 0.3s, transform 0.3s, left 0.3s;
  overflow-x: hidden;
  z-index: 1001;
}

@media (max-width: 768px) {
  .aside-menu {
    position: fixed;
    height: 100%;
    left: 0;
  }
  .aside-menu.is-mobile-hidden {
    transform: translateX(-100%);
  }
  .aside-menu.is-mobile-show {
    transform: translateX(0);
    box-shadow: 2px 0 8px rgba(0,0,0,0.15);
  }

  .mobile-mask {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.45);
    z-index: 1000;
  }

  .main-content {
    padding: 12px !important;
  }

  .u-hidden-mobile {
    display: none !important;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 全局响应式辅助类 */
.u-hidden-mobile {
  display: inline-flex;
}

.header-nav {
  background-color: var(--app-header-bg);
  border-bottom: 1px solid var(--app-border-color);
  padding: 0;
}

.main-content {
  background-color: var(--app-content-bg);
  padding: 20px;
}

.login-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--app-bg);
  position: relative;
  overflow: hidden;
}

.login-layout::before {
  content: "";
  position: absolute;
  top: -10%;
  right: -5%;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(14, 165, 233, 0.05) 0%, transparent 70%);
  border-radius: 50%;
  z-index: 0;
}

.login-layout::after {
  content: "";
  position: absolute;
  bottom: -10%;
  left: -5%;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(14, 165, 233, 0.08) 0%, transparent 70%);
  border-radius: 50%;
  z-index: 0;
}

.login-layout > * {
  position: relative;
  z-index: 1;
}
</style>
