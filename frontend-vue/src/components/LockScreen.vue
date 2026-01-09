<template>
  <Transition name="fade">
    <div v-if="ui.isLocked" class="lock-screen" role="dialog" aria-modal="true">
      <div class="lock-screen__content">
        <div class="lock-screen__avatar">
          <el-icon :size="64" color="#0ea5e9"><UserFilled /></el-icon>
        </div>
        <h2 class="lock-screen__title">屏幕已锁定</h2>
        <div class="lock-screen__form">
          <el-input
            v-model="password"
            type="password"
            placeholder="请输入解锁密码"
            show-password
            @keyup.enter="onUnlock"
            size="large"
          />
          <el-button type="primary" size="large" @click="onUnlock" class="lock-btn">
            解锁
          </el-button>
          <el-button link @click="onBackToLogin">
            返回登录
          </el-button>
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
import { UserFilled } from '@element-plus/icons-vue';

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

.lock-btn {
  font-weight: 600;
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
