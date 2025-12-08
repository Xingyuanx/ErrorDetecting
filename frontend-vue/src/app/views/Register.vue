<template>
  <section class="layout__section">
    <div class="layout__page-header"><h2 class="layout__page-title">新用户注册</h2></div>
    <form class="layout__grid" @submit.prevent="onSubmit">
      <input v-model.trim="username" placeholder="账号" class="header__search-input" />
      <input v-model.trim="password" type="password" placeholder="密码" class="header__search-input" />
      <input v-model.trim="confirm" type="password" placeholder="确认密码" class="header__search-input" />
      <input v-model.trim="email" placeholder="邮箱" class="header__search-input" />
      <input v-model.trim="fullName" placeholder="姓名" class="header__search-input" />
      <button class="btn">提交</button>
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
const confirm = ref('')
const email = ref('')
const fullName = ref('')
const role = ref('operator')
const msg = ref('')
const router = useRouter()
const auth = useAuthStore()
async function onSubmit() {
  if (!username.value || !password.value || !confirm.value || !email.value || !fullName.value) { msg.value = '请填写所有必填字段'; return }
  if (password.value !== confirm.value) { msg.value = '两次密码不一致'; return }
  const r = await auth.register(username.value, email.value, password.value, fullName.value)
  if (r.ok) router.replace({ name: auth.defaultPage })
  else msg.value = r.message || '注册失败'
}
</script>
