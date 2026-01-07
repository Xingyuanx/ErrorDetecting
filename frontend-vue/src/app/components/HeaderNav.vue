<template>
  <div class="header-container">
    <div class="header-left">
      <el-button
        v-if="!hideSidebar"
        class="toggle-btn"
        link
        @click="toggleSidebar"
      >
        <el-icon :size="20">
          <Expand v-if="ui.sidebarHidden" />
          <Fold v-else />
        </el-icon>
      </el-button>
      <el-breadcrumb separator="/" class="u-hidden-mobile">
        <el-breadcrumb-item v-for="(item, index) in breadcrumbs" :key="index" :to="item.path">
          {{ item.label }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="header-right">
      <el-tooltip content="刷新页面" placement="bottom">
        <el-button link @click="refreshPage" class="u-hidden-mobile">
          <el-icon :size="20"><Refresh /></el-icon>
        </el-button>
      </el-tooltip>

      <el-tooltip :content="isDark ? '切换到浅色模式' : '切换到暗黑模式'" placement="bottom">
        <el-button link @click="toggleThemeWithAnimation" class="theme-toggle-btn">
          <el-icon :size="20">
            <Moon v-if="!isDark" />
            <Sunny v-else />
          </el-icon>
        </el-button>
      </el-tooltip>

      <el-tooltip :content="isFullscreen ? '退出全屏' : '全屏显示'" placement="bottom">
        <el-button link @click="toggleFullscreen" class="u-hidden-mobile">
          <el-icon :size="20">
            <FullScreen v-if="!isFullscreen" />
            <Aim v-else />
          </el-icon>
        </el-button>
      </el-tooltip>

      <el-dropdown v-if="authed" trigger="click" @command="handleCommand">
        <div class="user-info">
          <el-avatar :size="32" icon="UserFilled" />
          <span class="username">{{ auth.user?.username }}</span>
          <el-icon class="el-icon--right"><arrow-down /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">个人主页</el-dropdown-item>
            <el-dropdown-item command="account">账号管理</el-dropdown-item>
            <el-dropdown-item divided command="lock">锁定屏幕</el-dropdown-item>
            <el-dropdown-item command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 锁屏密码设置弹窗 -->
    <el-dialog
      v-model="showLockModal"
      title="设置锁屏密码"
      :width="isMobile ? '90%' : '300px'"
      center
      append-to-body
    >
      <el-input
        v-model="lockPasswordInput"
        type="password"
        placeholder="请输入锁屏密码"
        show-password
        @keyup.enter="handleLock"
      />
      <template #footer>
        <el-button @click="showLockModal = false">取消</el-button>
        <el-button type="primary" @click="handleLock">锁定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import { useAuthStore } from "../stores/auth";
import { useUIStore } from "../stores/ui";
import { Expand, Fold, Refresh, FullScreen, Aim, UserFilled, ArrowDown, Moon, Sunny } from '@element-plus/icons-vue'

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const ui = useUIStore();
const { isAuthenticated } = storeToRefs(auth);
const { isDark } = storeToRefs(ui);
const authed = isAuthenticated;

const breadcrumbs = computed(() => {
  if (route.meta && route.meta.breadcrumb) {
    return route.meta.breadcrumb as Array<{ label: string, path: string }>;
  }
  const name = route.name ? String(route.name).toUpperCase() : '';
  return [
    { label: '首页', path: '/' },
    name ? { label: name, path: route.path } : null
  ].filter((i): i is { label: string, path: string } => i !== null);
});

const hideSidebar = computed(() => !!(route.meta && (route.meta as any).hideSidebar));

const isMobile = ref(window.innerWidth < 768);
const updateWidth = () => {
  isMobile.value = window.innerWidth < 768;
};

function toggleSidebar() {
  ui.toggleSidebar();
}

function toggleThemeWithAnimation(event: MouseEvent) {
  const isAppearanceTransition = (document as any).startViewTransition &&
    !window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (!isAppearanceTransition) {
    ui.toggleTheme();
    return;
  }

  const x = event.clientX;
  const y = event.clientY;
  const endRadius = Math.hypot(
    Math.max(x, innerWidth - x),
    Math.max(y, innerHeight - y)
  );

  const transition = (document as any).startViewTransition(async () => {
    ui.toggleTheme();
  });

  transition.ready.then(() => {
    const clipPath = [
      `circle(0px at ${x}px ${y}px)`,
      `circle(${endRadius}px at ${x}px ${y}px)`,
    ];
    document.documentElement.animate(
      {
        clipPath: isDark.value ? [...clipPath].reverse() : clipPath,
      },
      {
        duration: 450,
        easing: 'ease-in-out',
        pseudoElement: isDark.value
          ? '::view-transition-old(root)'
          : '::view-transition-new(root)',
      }
    );
  });
}

function refreshPage() {
  window.location.reload();
}

const isFullscreen = ref(false);
function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(() => {});
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen();
    }
  }
}

function updateFullscreenStatus() {
  isFullscreen.value = !!document.fullscreenElement;
}

onMounted(() => {
  document.addEventListener('fullscreenchange', updateFullscreenStatus);
  window.addEventListener('resize', updateWidth);
});

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', updateFullscreenStatus);
  window.removeEventListener('resize', updateWidth);
});

const showLockModal = ref(false);
const lockPasswordInput = ref('');

function handleLock() {
  if (lockPasswordInput.value) {
    ui.lock(lockPasswordInput.value);
    showLockModal.value = false;
    lockPasswordInput.value = '';
  }
}

function handleCommand(command: string) {
  switch (command) {
    case 'profile':
      router.push('/profile');
      break;
    case 'account':
      router.push('/account');
      break;
    case 'lock':
      showLockModal.value = true;
      break;
    case 'logout':
      auth.logout();
      router.replace({ name: 'login' });
      break;
  }
}
</script>

<style scoped>
.header-container {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f1f5f9;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}

:deep(.dark) .username {
  color: #cbd5e1;
}

html.dark .username {
  color: #cbd5e1;
}

.toggle-btn {
  padding: 8px;
  height: auto;
}

.theme-toggle-btn {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 50%;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.theme-toggle-btn:hover {
  background-color: var(--el-fill-color-light);
  transform: rotate(15deg) scale(1.1);
}

.theme-toggle-btn:active {
  transform: scale(0.95);
}

.theme-toggle-btn :deep(.el-icon) {
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.theme-toggle-btn:hover :deep(.el-icon) {
  color: var(--el-color-primary);
}

@media (max-width: 768px) {
  .u-hidden-mobile {
    display: none;
  }
}
</style>
