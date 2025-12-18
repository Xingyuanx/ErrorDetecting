<template>
  <section class="login">
    <div class="login__card">
      <div class="login__brand">
        <h1 class="login__title">集群管理系统</h1>
        <p class="login__subtitle">统一登录入口，自动识别用户类型</p>
      </div>
      <form class="login__form" @submit.prevent="onSubmit">
        <input v-model.trim="username" placeholder="账号" autocomplete="username" class="header__search-input login__input" />
        <input v-model.trim="password" type="password" placeholder="密码" autocomplete="current-password" class="header__search-input login__input" />
        <button class="btn btn--primary login__btn" :disabled="loading">{{ loading ? '登录中...' : '登录' }}</button>
        <RouterLink class="btn login__btn" to="/register">新用户注册</RouterLink>
      </form>
      <div class="login__hint">演示账户：账号 123，密码 123，权限：管理员</div>
      <div v-if="msg" class="login__msg">{{ msg }}</div>
      <div class="login__health" :data-status="health">
        后端连接：{{ health === 'ok' ? '正常' : health === 'fail' ? '异常' : '检测中' }}
      </div>
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

<style scoped>
.login{ display:flex; align-items:center; justify-content:center; min-height: 70vh }
.login__card{ width: 420px; max-width: 100%; background:#fff; border:1px solid #e5e7eb; border-radius:12px; box-shadow:0 12px 32px rgba(16,24,40,0.12); padding:20px }
.login__brand{ text-align:center; margin-bottom:16px }
.login__title{ font-size:22px; font-weight:700 }
.login__subtitle{ color:#6b7280; margin-top:4px }
.login__form{ display:flex; flex-direction:column; gap:10px; margin-top:8px }
.login__input{ width:100% }
.login__btn{ width:100%; display:flex; justify-content:center }
.login__hint{ font-size:12px; color:#a16207; background:#fef3c7; border:1px solid #fde68a; border-radius:8px; padding:8px; margin-top:10px }
.login__msg{ font-size:12px; color:#dc2626; margin-top:8px }
.login__health{ font-size:12px; margin-top:8px; color:#6b7280 }
.login__health[data-status="ok"]{ color:#16a34a }
.login__health[data-status="fail"]{ color:#dc2626 }
@media (max-width: 480px){
  .login__card{ width: 92% }
}
</style>
