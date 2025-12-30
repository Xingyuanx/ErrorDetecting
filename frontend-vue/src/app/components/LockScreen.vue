<template>
  <Transition name="fade">
    <div v-if="ui.isLocked" class="lock-screen" role="dialog" aria-modal="true">
      <div class="lock-screen__content">
        <div class="lock-screen__avatar">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 1024 1024"
            width="64"
            height="64"
          >
            <path
              fill="currentColor"
              d="M512 512a192 192 0 1 0 0-384 192 192 0 0 0 0 384m0 64a256 256 0 1 1 0-512 256 256 0 0 1 0 512m320 320v-96a96 96 0 0 0-96-96H288a96 96 0 0 0-96 96v96a32 32 0 1 1-64 0v-96a160 160 0 0 1 160-160h448a160 160 0 0 1 160 160v96a32 32 0 1 1-64 0"
            ></path>
          </svg>
        </div>
        <h2 class="lock-screen__title">屏幕已锁定</h2>
        <div class="lock-screen__form">
          <input
            v-model="password"
            type="password"
            class="lock-screen__input"
            placeholder="请输入解锁密码"
            @keyup.enter="onUnlock"
          />
          <button class="lock-screen__btn lock-screen__btn--primary" @click="onUnlock">
            解锁
          </button>
          <button class="lock-screen__btn lock-screen__btn--link" @click="onBackToLogin">
            返回登录
          </button>
        </div>
        <p v-if="error" class="lock-screen__error">{{ error }}</p>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useUIStore } from '../stores/ui';
import { useAuthStore } from '../stores/auth';

const ui = useUIStore();
const auth = useAuthStore();
const router = useRouter();

const password = ref('');
const error = ref('');

function onUnlock() {
  if (password.value === ui.lockPassword) {
    ui.unlock();
    password.value = '';
    error.value = '';
  } else {
    error.value = '密码错误';
    password.value = '';
  }
}

function onBackToLogin() {
  ui.unlock();
  auth.logout();
  router.replace({ name: 'login' });
}
</script>

<style scoped>
.lock-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.9);
  backdrop-filter: blur(10px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.lock-screen__content {
  width: 100%;
  max-width: 320px;
  text-align: center;
}

.lock-screen__avatar {
  margin-bottom: 24px;
  color: var(--accent, #58bc82);
  display: flex;
  justify-content: center;
  align-items: center;
}

.lock-screen__title {
  font-size: 24px;
  margin-bottom: 32px;
  font-weight: 600;
}

.lock-screen__form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.lock-screen__input {
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 16px;
  outline: none;
  transition: all 0.3s;
}

.lock-screen__input:focus {
  border-color: var(--accent, #58bc82);
  background: rgba(255, 255, 255, 0.15);
}

.lock-screen__btn {
  padding: 12px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.lock-screen__btn--primary {
  background: var(--accent, #58bc82);
  color: white;
}

.lock-screen__btn--primary:hover {
  filter: brightness(1.1);
}

.lock-screen__btn--link {
  background: transparent;
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  text-decoration: underline;
}

.lock-screen__btn--link:hover {
  color: white;
}

.lock-screen__error {
  color: #f43f5e;
  margin-top: 16px;
  font-size: 14px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
