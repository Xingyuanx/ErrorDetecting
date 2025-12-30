<template>
  <header class="header" role="banner">
    <div class="header__left">
      <button
        v-if="!hideSidebar"
        class="btn sidebar-toggle"
        type="button"
        @click="toggleSidebar"
        :title="ui.sidebarHidden ? '展开侧边栏' : '收起侧边栏'"
      >
        <svg
          viewBox="0 0 24 24"
          width="24"
          height="24"
          stroke="currentColor"
          stroke-width="2"
          fill="none"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <line x1="3" y1="12" x2="21" y2="12"></line>
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <line x1="3" y1="18" x2="21" y2="18"></line>
        </svg>
      </button>
      <nav class="header__nav" role="navigation" aria-label="主导航"></nav>
    </div>
    <div class="header__right">
      <div v-if="!hideSidebar" class="header__search">
        <!-- From Uiverse.io by 0xnihilism -->
        <div class="input-container">
          <input
            id="global-search"
            class="input"
            name="text"
            type="text"
            placeholder="搜索节点、日志或配置..."
          />
        </div>
      </div>
      <!-- 刷新页面按钮 -->
      <button
        class="btn refresh-toggle"
        type="button"
        @click="refreshPage"
        title="刷新页面"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 1024 1024"
          width="20"
          height="20"
        >
          <path
            fill="currentColor"
            d="M784.512 230.272v-50.56a32 32 0 1 1 64 0v149.056a32 32 0 0 1-32 32H667.52a32 32 0 1 1 0-64h92.992A320 320 0 1 0 524.8 833.152a320 320 0 0 0 320-320h64a384 384 0 0 1-384 384 384 384 0 0 1-384-384 384 384 0 0 1 643.712-282.88"
          ></path>
        </svg>
      </button>

      <!-- 全屏切换按钮 -->
      <button
        class="btn fullscreen-toggle u-hidden-mobile"
        type="button"
        @click="toggleFullscreen"
        :title="isFullscreen ? '退出全屏' : '全屏显示'"
      >
        <svg
          v-if="!isFullscreen"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 1024 1024"
          width="20"
          height="20"
        >
          <path
            fill="currentColor"
            d="M128 128h256v64H192v192h-64V128zm0 768V640h64v192h192v64H128zm768 0H640v-64h192V640h64v256zm0-768v256h-64V192H640v-64h256z"
          ></path>
        </svg>
        <svg
          v-else
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 1024 1024"
          width="20"
          height="20"
        >
          <path
            fill="currentColor"
            d="M128 320h192V128h64v256H128v-64zm192 384H128v-64h256v256h-64V704zm384 0v192h-64V640h256v64H704zm0-384V128h64v256h256v64H640V320z"
          ></path>
        </svg>
      </button>

      <div class="header__user-menu" v-if="authed">
        <button class="header__user-avatar" type="button">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 1024 1024"
            width="20"
            height="20"
          >
            <path
              fill="currentColor"
              d="M512 512a192 192 0 1 0 0-384 192 192 0 0 0 0 384m0 64a256 256 0 1 1 0-512 256 256 0 0 1 0 512m320 320v-96a96 96 0 0 0-96-96H288a96 96 0 0 0-96 96v96a32 32 0 1 1-64 0v-96a160 160 0 0 1 160-160h448a160 160 0 0 1 160 160v96a32 32 0 1 1-64 0"
            ></path>
          </svg>
        </button>
        <div class="header__user-dropdown" role="menu">
          <RouterLink
            class="header__user-dropdown-item"
            to="/profile"
            role="menuitem"
            >个人主页</RouterLink
          >
          <RouterLink
            class="header__user-dropdown-item"
            to="/account"
            role="menuitem"
            >账号管理</RouterLink
          >
          <a
            class="header__user-dropdown-item"
            href="javascript:;"
            role="menuitem"
            @click.prevent="showLockModal = true"
            >锁定屏幕</a
          >
          <a
            class="header__user-dropdown-item"
            href="javascript:;"
            role="menuitem"
            @click.prevent="onLogout"
            >退出登录</a
          >
        </div>
      </div>
    </div>
  </header>

  <!-- 锁屏密码设置弹窗 -->
  <Transition name="fade">
    <div v-if="showLockModal" class="modal-overlay" @click.self="showLockModal = false">
      <div class="modal-content">
        <h3 class="modal-title">设置锁屏密码</h3>
        <input
          v-model="lockPasswordInput"
          type="password"
          class="modal-input"
          placeholder="请输入锁屏密码"
          @keyup.enter="handleLock"
        />
        <div class="modal-actions">
          <button class="modal-btn modal-btn--secondary" @click="showLockModal = false">
            取消
          </button>
          <button class="modal-btn modal-btn--primary" @click="handleLock">
            锁定
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { RouterLink } from "vue-router";
import { storeToRefs } from "pinia";
import { useAuthStore } from "../stores/auth";
import { useUIStore } from "../stores/ui";
import { Roles } from "../constants/roles";
const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const { isAuthenticated, role } = storeToRefs(auth);
function isActive(p: string) {
  return route.path === p;
}
const authed = isAuthenticated;
function can(roles: string[]) {
  return roles.includes(role.value || "");
}
function onLogout() {
  auth.logout();
  router.replace({ name: "login" });
}
const ui = useUIStore();
const showLockModal = ref(false);
const lockPasswordInput = ref('');

function handleLock() {
  if (lockPasswordInput.value) {
    ui.lock(lockPasswordInput.value);
    showLockModal.value = false;
    lockPasswordInput.value = '';
  }
}

function toggleSidebar() {
  ui.toggleSidebar();
}

function refreshPage() {
  window.location.reload();
}

// 全屏逻辑
const isFullscreen = ref(false);
function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch((err) => {
      console.error(
        `Error attempting to enable full-screen mode: ${err.message}`
      );
    });
  } else {
    document.exitFullscreen();
  }
}

// 监听全屏变化状态，同步图标
function handleFullscreenChange() {
  isFullscreen.value = !!document.fullscreenElement;
}

const hideSidebar = computed(
  () => !!(route.meta && (route.meta as any).hideSidebar)
);
function onDocClick() {
  closeAll();
}
onMounted(() => {
  document.addEventListener("click", onDocClick);
  document.addEventListener("fullscreenchange", handleFullscreenChange);
});
onUnmounted(() => {
  document.removeEventListener("click", onDocClick);
  document.removeEventListener("fullscreenchange", handleFullscreenChange);
});
function closeAll() {}
</script>

<style scoped>
/* From Uiverse.io by 0xnihilism */
.input-container {
  position: relative;
  width: 100%;
  max-width: 270px;
}

.input {
  width: 100%;
  height: 40px; /* 原 CSS 是 60px，为了适配 Header 高度调整为 40px */
  padding: 8px 12px; /* 调整 padding */
  font-size: 14px; /* 调整字体大小 */
  font-family: "Courier New", monospace;
  color: #000;
  background-color: #fff;
  border: 2px solid #000; /* 减小边框粗细 */
  border-radius: 0;
  outline: none;
  transition: all 0.3s ease;
  box-shadow: 4px 4px 0 #000; /* 调整阴影大小 */
}

.input::placeholder {
  color: #888;
}

.input:hover {
  transform: translate(-2px, -2px); /* 调整位移 */
  box-shadow: 6px 6px 0 #000; /* 调整 hover 阴影 */
}

.input:focus {
  background-color: #010101;
  color: #fff;
  border-color: #d6d9dd;
}

.sidebar-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--text-primary);
}

.sidebar-toggle:hover {
  background: var(--hover);
  border-color: var(--accent);
  color: var(--accent);
}

.refresh-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--text-primary);
  width: 40px;
  height: 40px;
}

.refresh-toggle:hover {
  background: var(--hover);
  border-color: var(--accent);
  color: var(--accent);
}

.refresh-toggle:active svg {
  transform: rotate(180deg);
  transition: transform 0.3s ease;
}

.fullscreen-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--text-primary);
  width: 40px;
  height: 40px;
}

.fullscreen-toggle:hover {
  background: var(--hover);
  border-color: var(--accent);
  color: var(--accent);
}

.input:focus::placeholder {
  color: #fff;
}

@keyframes shake {
  0% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-5px) rotate(-5deg);
  }
  50% {
    transform: translateX(5px) rotate(5deg);
  }
  75% {
    transform: translateX(-5px) rotate(-5deg);
  }
  100% {
    transform: translateX(0);
  }
}

.input:focus {
  animation: shake 0.5s ease-in-out;
}

@keyframes glitch {
  0% {
    transform: none;
    opacity: 1;
  }
  7% {
    transform: skew(-0.5deg, -0.9deg);
    opacity: 0.75;
  }
  10% {
    transform: none;
    opacity: 1;
  }
  27% {
    transform: none;
    opacity: 1;
  }
  30% {
    transform: skew(0.8deg, -0.1deg);
    opacity: 0.75;
  }
  35% {
    transform: none;
    opacity: 1;
  }
  52% {
    transform: none;
    opacity: 1;
  }
  55% {
    transform: skew(-1deg, 0.2deg);
    opacity: 0.75;
  }
  50% {
    transform: none;
    opacity: 1;
  }
  72% {
    transform: none;
    opacity: 1;
  }
  75% {
    transform: skew(0.4deg, 1deg);
    opacity: 0.75;
  }
  80% {
    transform: none;
    opacity: 1;
  }
  100% {
    transform: none;
    opacity: 1;
  }
}

.input:not(:placeholder-shown) {
  animation: glitch 1s linear infinite;
}

.input-container::after {
  content: "|";
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #000;
  animation: blink 0.7s step-end infinite;
  pointer-events: none; /* 防止遮挡输入点击 */
}

@keyframes blink {
  50% {
    opacity: 0;
  }
}

.input:focus + .input-container::after {
  /* 这里无法选中伪元素，需要调整结构或 JS，但伪元素是 input-container 的。input focus 时，input-container 的伪元素无法直接变色，除非 input-container 有 focus-within */
  color: #fff;
}
/* 使用 focus-within 替代 */
.input-container:focus-within::after {
  color: #fff;
}

.input:not(:placeholder-shown) {
  font-weight: bold;
  letter-spacing: 1px;
  text-shadow: 0px 0px 0 #000;
}

.header__dropdown {
  position: relative;
}
.header__dropdown-trigger {
  display: flex;
  align-items: center;
  gap: 6px;
}
.header__dropdown-icon {
  font-size: 12px;
  transition: transform 120ms ease;
}
.icon-rot {
  transform: rotate(180deg);
}
.header__dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 4px;
  width: 12rem;
  background: var(--surface);
  border-radius: 8px;
  box-shadow: 0 12px 32px rgba(16, 24, 40, 0.12);
  padding: 4px 0;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-8px);
  transition: all 120ms ease;
}
.header__dropdown-menu--show {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}
.header__dropdown-item {
  display: block;
  padding: 8px 12px;
  border-radius: 6px;
}
.header__dropdown-item:hover {
  background: var(--hover);
}

.header__search {
  display: flex;
  align-items: center;
  position: relative;
} /* 移除 margin 以统一使用 gap */
.header {
  position: relative;
  z-index: 50;
}
.header__user-menu {
  position: relative;
  z-index: 100;
}
.header__user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 0;
}

.header__user-avatar:hover {
  background: var(--hover);
  border-color: var(--accent);
  color: var(--accent);
}
.header__user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 4px;
  width: 12rem;
  background: var(--surface);
  border-radius: 8px;
  box-shadow: 0 12px 32px rgba(16, 24, 40, 0.2);
  padding: 4px 0;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-8px);
  transition: all 120ms ease;
  z-index: 1000;
}
.header__user-menu:hover .header__user-dropdown {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}
.header__user-dropdown-item {
  display: block;
  padding: 8px 12px;
  border-radius: 6px;
}
.header__user-dropdown-item:hover {
  background: var(--hover);
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: var(--surface, #fff);
  padding: 24px;
  border-radius: 12px;
  width: 100%;
  max-width: 360px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  color: var(--text-primary);
}

.modal-input {
  width: 100%;
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid var(--border, #e5e7eb);
  background: var(--bg-light, #f9fafb);
  margin-bottom: 24px;
  outline: none;
  transition: all 0.2s;
}

.modal-input:focus {
  border-color: var(--accent, #58bc82);
  box-shadow: 0 0 0 3px rgba(88, 188, 130, 0.1);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.modal-btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.modal-btn--secondary {
  background: var(--bg-light, #f3f4f6);
  color: var(--text-secondary, #4b5563);
}

.modal-btn--secondary:hover {
  background: var(--hover, #e5e7eb);
}

.modal-btn--primary {
  background: var(--accent, #58bc82);
  color: white;
}

.modal-btn--primary:hover {
  filter: brightness(1.1);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
