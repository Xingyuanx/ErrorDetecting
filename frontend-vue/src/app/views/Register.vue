<template>
  <section class="register">
    <div class="register__card">
      <div class="register__brand">
        <h1 class="register__title">ClusterManager新用户注册</h1>
      </div>
      <form class="register__form" @submit.prevent="onSubmit">
        <input v-model.trim="username" placeholder="账号" autocomplete="username" class="header__search-input register__input" />
        <input v-model.trim="password" type="password" placeholder="密码" autocomplete="new-password" class="header__search-input register__input" />
        <input v-model.trim="confirm" type="password" placeholder="确认密码" autocomplete="new-password" class="header__search-input register__input" />
        <input v-model.trim="email" type="email" placeholder="邮箱" autocomplete="email" class="header__search-input register__input" />
        <input v-model.trim="fullName" placeholder="姓名" class="header__search-input register__input" />
        <button class="btn btn--primary register__btn" :disabled="loading">{{ loading ? '提交中...' : '提交' }}</button>
        <RouterLink class="btn register__btn" to="/login">返回登录</RouterLink>
      </form>
      <div v-if="msg" class="register__msg">{{ msg }}</div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
const username = ref('')
const password = ref('')
const confirm = ref('')
const email = ref('')
const fullName = ref('')
const role = ref('operator')
const msg = ref('')
const loading = ref(false)
const router = useRouter()
const auth = useAuthStore()
async function onSubmit() {
  loading.value = true
  if (!username.value || !password.value || !confirm.value || !email.value || !fullName.value) { msg.value = '请填写所有必填字段'; return }
  if (password.value !== confirm.value) { msg.value = '两次密码不一致'; return }
  const r = await auth.register(username.value, email.value, password.value, fullName.value)
  if (r.ok) router.replace({ name: auth.defaultPage })
  else msg.value = r.message || '注册失败'
  loading.value = false
}
</script>

<style scoped>
.register{ display:flex; align-items:center; justify-content:center; min-height: 70vh }
.register__card{ width: 480px; max-width: 100%; background:#fff; border:1px solid #e5e7eb; border-radius:12px; box-shadow:0 12px 32px rgba(16,24,40,0.12); padding:20px }
.register__brand{ text-align:center; margin-bottom:16px }
.register__title{ font-size:22px; font-weight:700 }
.register__form{ display:flex; flex-direction:column; gap:10px; margin-top:8px }
.register__input{ width:100% }
.register__btn{ width:100% }
.register__msg{ font-size:12px; color:#dc2626; margin-top:8px }
@media (max-width: 480px){
  .register__card{ width: 92% }
}
</style>
