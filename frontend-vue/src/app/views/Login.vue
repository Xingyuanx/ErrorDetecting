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
    <div class="u-text-sm" :class="health === 'ok' ? 'u-text-green-600' : health === 'fail' ? 'u-text-red-600' : 'u-text-gray-600'">
      后端连接：{{ health === 'ok' ? '正常' : health === 'fail' ? '异常' : '检测中' }}
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../lib/api'
const username = ref('')
const password = ref('')
const msg = ref('')
const loading = ref(false)
const health = ref<'ok'|'fail'|'checking'>('checking')
const router = useRouter()
const auth = useAuthStore()
onMounted(async () => {
  try { await api.get('/v1/health'); health.value = 'ok' } catch { health.value = 'fail' }
})
async function onSubmit() {
  loading.value = true
  const r = await auth.login(username.value, password.value)
  loading.value = false
  if (r.ok) router.replace({ name: auth.defaultPage })
  else msg.value = r.message || '登录失败'
}
</script>
