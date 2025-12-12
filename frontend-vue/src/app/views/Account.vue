<template>
  <section class="layout__section">
    <div class="layout__page-header exec-header">
      <div>
        <h2 class="layout__page-title">账号管理（原型）</h2>
        <div class="layout__page-subtitle">修改密码、设置双因素认证等</div>
      </div>
      <div class="layout__page-actions"><button class="btn btn--primary" type="button" @click="save">保存设置</button></div>
    </div>

    <article class="layout__card u-mt-2">
      <div class="layout__card-header"><h3 class="layout__card-title">安全设置</h3></div>
      <div class="layout__card-body">
        <form class="layout__grid layout__grid--3" @submit.prevent="save">
          <div>
            <label class="u-text-sm u-font-medium u-text-gray-700">当前密码</label>
            <input v-model.trim="form.current" type="password" class="u-w-full u-p-2 u-border u-rounded u-mt-1" placeholder="••••••••" autocomplete="current-password" />
          </div>
          <div>
            <label class="u-text-sm u-font-medium u-text-gray-700">新密码</label>
            <input v-model.trim="form.next" type="password" class="u-w-full u-p-2 u-border u-rounded u-mt-1" placeholder="至少8位" autocomplete="new-password" />
          </div>
          <div>
            <label class="u-text-sm u-font-medium u-text-gray-700">确认新密码</label>
            <input v-model.trim="form.confirm" type="password" class="u-w-full u-p-2 u-border u-rounded u-mt-1" placeholder="再次输入" autocomplete="new-password" />
          </div>
        </form>
        <div class="u-text-sm u-text-gray-700 u-mt-2" role="alert">{{ err }}</div>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
const form = reactive({ current:'', next:'', confirm:'' })
const err = ref('')
function save(){
  err.value = ''
  if (!form.current || !form.next || !form.confirm) { err.value = '请填写完整密码信息'; return }
  if (form.next.length < 8) { err.value = '新密码至少8位'; return }
  if (form.next !== form.confirm) { err.value = '两次输入的新密码不一致'; return }
  err.value = '已保存（示例界面，未接入后端）'
}
</script>

<style scoped>
.exec-header{ display:flex; justify-content:space-between; align-items:center }
.layout__page-subtitle{ color:#6b7280; font-size:13px }
.layout__card{ background:#ffffff; border:1px solid #e5e7eb; border-radius:12px; box-shadow:0 8px 24px rgba(16,24,40,0.06) }
.layout__card-header{ padding:12px 16px; border-bottom:1px solid #e5e7eb }
.layout__card-title{ font-size:14px; font-weight:600 }
.layout__card-body{ padding:16px }
.layout__grid{ display:grid; gap:16px }
.layout__grid--3{ grid-template-columns: 1fr 1fr 1fr }
</style>
