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
          <!-- From Uiverse.io by vinodjangid07 -->
          <button class="Btn logout-btn" @click.prevent="onLogout">
            <div class="sign">
              <svg viewBox="0 0 512 512">
                <path
                  d="M377.9 105.9L500.7 228.7c7.2 7.2 11.3 17.1 11.3 27.3s-4.1 20.1-11.3 27.3L377.9 406.1c-6.4 6.4-15 9.9-24 9.9c-18.7 0-33.9-15.2-33.9-33.9l0-62.1-128 0c-17.7 0-32-14.3-32-32l0-64c0-17.7 14.3-32 32-32l128 0 0-62.1c0-18.7 15.2-33.9 33.9-33.9c9 0 17.6 3.6 24 9.9zM160 96L96 96c-17.7 0-32 14.3-32 32l0 256c0 17.7 14.3 32 32 32l64 0c17.7 0 32 14.3 32 32s-14.3 32-32 32l-64 0c-53 0-96-43-96-96L0 128C0 75 43 32 96 32l64 0c17.7 0 32 14.3 32 32s-14.3 32-32 32z"
                ></path>
              </svg>
            </div>
            <div class="text">退出登录</div>
          </button>
        </div>
      </div>
    </div>
  </header>
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

/* From Uiverse.io by kennyotsu-monochromia */
.logout-btn {
  margin: 8px 12px; /* 增加一些外边距以适应菜单 */
}
.Btn {
  --black: #000000;
  --ch-black: #141414;
  --eer-black: #1b1b1b;
  --night-rider: #2e2e2e;
  --white: #ffffff;
  --af-white: #f3f3f3;
  --ch-white: #e1e1e1;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 45px;
  height: 45px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition-duration: 0.3s;
  box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.199);
  background-color: var(--af-white);
}

/* plus sign */
.sign {
  width: 100%;
  transition-duration: 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sign svg {
  width: 17px;
}

.sign svg path {
  fill: var(--night-rider);
}
/* text */
.text {
  position: absolute;
  right: 0%;
  width: 0%;
  opacity: 0;
  color: var(--night-rider);
  font-size: 1.2em;
  font-weight: 600;
  transition-duration: 0.3s;
  white-space: nowrap;
}
/* hover effect on button width */
.Btn:hover {
  width: 125px;
  border-radius: 5px;
  transition-duration: 0.3s;
}

.Btn:hover .sign {
  width: 30%;
  transition-duration: 0.3s;
  padding-left: 20px;
}
/* hover effect button's text */
.Btn:hover .text {
  opacity: 1;
  width: 70%;
  transition-duration: 0.3s;
  padding-right: 10px;
}
/* button click effect*/
.Btn:active {
  transform: translate(2px, 2px);
}
</style>
