<template>
  <section class="layout__section">
    <div class="layout__page-header exec-header">
      <div>
        <h2 class="layout__page-title">个人主页</h2>
        <div class="layout__page-subtitle">查看与管理个人基础信息</div>
      </div>
      <div class="layout__page-actions"><button class="btn" disabled>编辑资料</button></div>
    </div>
    <article class="layout__card u-mt-2">
      <div class="layout__card-header"><h3 class="layout__card-title">个人信息</h3></div>
      <div class="layout__card-body">
        <div v-if="loading" class="u-text-sm u-text-gray-700">正在加载...</div>
        <div v-else-if="err" class="u-text-sm" style="color:#dc2626">{{ err }}</div>
        <div v-else class="layout__grid layout__grid--3">
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
import { RoleLabel } from '../constants/roles'
const auth = useAuthStore()
const { user, token } = storeToRefs(auth)
const username = ref('')
const email = ref('')
const roleName = ref('')
const loading = ref(true)
const err = ref('')
function normalizeRole(r: string): 'admin'|'operator'|'observer' {
  const v = String(r || '').trim().toLowerCase()
  if (v === 'admin' || v === 'administrator') return 'admin'
  if (v === 'operator' || v === 'ops' || v === 'op') return 'operator'
  return 'observer'
}
onMounted(async () => {
  loading.value = true
  err.value = ''
  try{
    const r = await api.get('/v1/users', { headers: token.value ? { Authorization: `Bearer ${token.value}` } : undefined })
    const list = Array.isArray(r?.data?.users) ? r.data.users : (Array.isArray(r?.data) ? r.data : [])
    const currentName = String(user.value?.username || '')
    const picked = (list || []).find((x:any) => String(x?.username || '') === currentName)
    if (!picked) { err.value = '未找到当前用户'; return }
    const name = String(picked?.username || '')
    const emailVal = String(picked?.email || '')
    const roleRaw = String(picked?.role || '')
    const roleKey = normalizeRole(roleRaw)
    username.value = name
    email.value = emailVal
    roleName.value = RoleLabel[roleKey as keyof typeof RoleLabel] || roleRaw || '观察员'
    if (name && name === currentName) { auth.user = { username: name, role: roleKey as any }; auth.persist() }
  }catch(e:any){
    const s = e?.response?.status
    err.value = s === 403 ? '权限不足，无法读取用户列表' : '个人信息加载失败'
  }finally{
    loading.value = false
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
