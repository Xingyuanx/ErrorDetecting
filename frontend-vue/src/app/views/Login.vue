<template>
  <section class="layout__section">
    <div class="layout__page-header">
      <h2 class="layout__page-title">用户登录</h2>
      <p class="layout__page-subtitle">统一登录入口，自动识别用户类型</p>
    </div>
    <form class="layout__grid" @submit.prevent="onSubmit">
      <input v-model.trim="username" placeholder="账号" autocomplete="username" class="header__search-input" />
      <input v-model.trim="password" type="password" placeholder="密码" autocomplete="current-password" class="header__search-input" />
      <button class="btn">登录</button>
      <RouterLink class="btn" to="/register">新用户注册</RouterLink>
    </form>
    <div class="u-text-sm u-text-gray-700">{{ msg }}</div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
const username = ref('')
const password = ref('')
const msg = ref('')
const router = useRouter()
const auth = useAuthStore()
function onSubmit() {
  const r = auth.login(username.value, password.value)
  if (r.ok) router.replace({ name: auth.defaultPage })
  else msg.value = r.message || '登录失败'
}
</script>

