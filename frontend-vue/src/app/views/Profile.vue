<template>
  <section class="layout__section">
    <div class="layout__page-header exec-header">
      <div>
        <h2 class="layout__page-title">个人主页（原型）</h2>
        <div class="layout__page-subtitle">查看与管理个人基础信息</div>
      </div>
      <div class="layout__page-actions"><button class="btn" disabled>编辑资料</button></div>
    </div>
    <article class="layout__card u-mt-2">
      <div class="layout__card-header"><h3 class="layout__card-title">个人信息</h3></div>
      <div class="layout__card-body">
        <div class="layout__grid layout__grid--3">
          <div>
            <span class="u-text-sm u-text-gray-700">用户名</span>
            <div class="u-font-medium u-mt-1">{{ username }}</div>
          </div>
          <div>
            <span class="u-text-sm u-text-gray-700">邮箱</span>
            <div class="u-font-medium u-mt-1">{{ email }}</div>
          </div>
          <div>
            <span class="u-text-sm u-text-gray-700">角色</span>
            <div class="u-font-medium u-mt-1">{{ roleName }}</div>
          </div>
        </div>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '../stores/auth'
import api from '../lib/api'
const auth = useAuthStore()
const { user, token } = storeToRefs(auth)
const username = ref('admin')
const email = ref('admin@example.com')
const roleName = ref('管理员')
onMounted(async () => {
  try{
    const r = await api.get('/v1/user/me', { headers: token.value ? { Authorization: `Bearer ${token.value}` } : undefined })
    const u = r?.data?.user || r?.data || {}
    const name = u?.username || user.value?.username || 'admin'
    username.value = name
    email.value = u?.email || `${name}@example.com`
    const roleKey = u?.role || user.value?.role || 'admin'
    roleName.value = roleKey==='admin'?'管理员': roleKey==='operator'?'操作员':'观察员'
  }catch(e:any){
    const name = user.value?.username || 'admin'
    username.value = name
    email.value = `${name}@example.com`
    const roleKey = user.value?.role || 'admin'
    roleName.value = roleKey==='admin'?'管理员': roleKey==='operator'?'操作员':'观察员'
  }
})
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
