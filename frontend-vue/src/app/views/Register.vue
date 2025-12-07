<template>
  <section class="layout__section">
    <div class="layout__page-header"><h2 class="layout__page-title">新用户注册</h2></div>
    <form class="layout__grid" @submit.prevent="onSubmit">
      <input v-model.trim="username" placeholder="账号" class="header__search-input" />
      <input v-model.trim="password" type="password" placeholder="密码" class="header__search-input" />
      <input v-model.trim="confirm" type="password" placeholder="确认密码" class="header__search-input" />
      <input v-model.trim="contact" placeholder="联系方式" class="header__search-input" />
      <select v-model="role" class="header__search-input"><option value="operator">操作员</option><option value="observer">观察员</option><option value="admin">管理员</option></select>
      <button class="btn">提交</button>
    </form>
    <div class="u-text-sm u-text-gray-700">{{ msg }}</div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const username = ref('')
const password = ref('')
const confirm = ref('')
const contact = ref('')
const role = ref('operator')
const msg = ref('')
function onSubmit() {
  if (!username.value || !password.value || !confirm.value || !contact.value) { msg.value = '请填写所有必填字段'; return }
  if (password.value !== confirm.value) { msg.value = '两次密码不一致'; return }
  msg.value = '提交成功，已进入审批队列'
}
</script>

