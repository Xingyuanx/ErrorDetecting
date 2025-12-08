<template>
  <section class="layout__section" aria-labelledby="role-assign-title">
    <header class="layout__page-header">
      <div>
        <h2 id="role-assign-title" class="layout__page-title"><i class="fas fa-user-tag"></i> 角色分配</h2>
        <p class="layout__page-subtitle">选择用户并指定其在系统中的角色</p>
      </div>
      <div class="layout__page-actions">
        <button class="btn btn--primary" @click="onSave" :disabled="!user || !role || loading">保存分配</button>
        <span class="u-text-sm u-ml-2" v-if="loading">提交中...</span>
      </div>
    </header>

    <article class="layout__card">
      <div class="layout__card-header">
        <h3 class="layout__card-title">选择与设置</h3>
      </div>
      <div class="layout__card-body">
        <div class="layout__grid layout__grid--2">
          <div>
            <label class="u-text-sm u-font-medium u-text-gray-700"><i class="fas fa-user"></i> 选择用户</label>
            <select class="u-w-full u-p-2 u-border u-rounded u-mt-1" v-model="user">
              <option v-for="u in users" :key="u" :value="u">{{ u }}</option>
            </select>
            <div class="u-text-sm u-text-gray-700 u-mt-1" v-if="!users.length">暂无用户，请先在用户管理中创建</div>
          </div>
          <div>
            <label class="u-text-sm u-font-medium u-text-gray-700"><i class="fas fa-id-badge"></i> 选择角色</label>
            <select class="u-w-full u-p-2 u-border u-rounded u-mt-1" v-model="role">
              <option value="admin">管理员</option>
              <option value="operator">操作员</option>
              <option value="observer">观察员</option>
            </select>
          </div>
        </div>
        <div class="u-text-sm u-mt-2" :class="msgClass">{{ msg }}</div>
      </div>
    </article>

    <article class="layout__card u-mt-4">
      <div class="layout__card-header">
        <h3 class="layout__card-title">当前选择</h3>
      </div>
      <div class="layout__card-body">
        <div class="u-text-sm u-text-gray-700">用户：<span class="u-font-medium">{{ user || '未选择' }}</span></div>
        <div class="u-text-sm u-text-gray-700 u-mt-1">角色：<span class="u-font-medium">{{ roleLabel }}</span></div>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '../lib/api'
import { useAuthStore } from '../stores/auth'
const auth = useAuthStore()
const users = ref<string[]>([])
const user = ref('')
const role = ref('operator')
const msg = ref('')
const loading = ref(false)
const msgClass = computed(() => (msg.value ? (msg.value.startsWith('成功') ? 'u-text-green-600' : 'u-text-error') : 'u-text-gray-600'))
const roleLabel = computed(() => (role.value === 'admin' ? '管理员' : role.value === 'operator' ? '操作员' : role.value === 'observer' ? '观察员' : '未选择'))
onMounted(async () => {
  try {
    const r = await api.get('/v1/users', { headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
    const list = Array.isArray(r.data?.users) ? r.data.users : []
    users.value = list.map((x: any) => x?.username).filter((s: any) => typeof s === 'string')
  } catch (e: any) {
    msg.value = e?.response?.data?.detail || '用户列表加载失败'
  }
})
async function onSave() {
  msg.value = ''
  if (!user.value || !role.value) { msg.value = '请选择用户与角色'; return }
  loading.value = true
  try {
    await api.patch(`/v1/users/${encodeURIComponent(user.value)}`, { role: role.value }, { headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
    msg.value = '成功：已更新用户角色'
  } catch (e: any) {
    const d = e?.response?.data
    const errs = d?.detail?.errors
    if (Array.isArray(errs) && errs.length) msg.value = errs.map((x: any) => x?.message || '').filter(Boolean).join('；')
    else msg.value = d?.detail || '角色分配失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.layout__section { background: #f8fafc; padding: 8px; border-radius: 8px }
.layout__page-header { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #e5e7eb }
.layout__page-title { font-size: 18px; font-weight: 700; display: flex; align-items: center; gap: 8px }
.layout__page-subtitle { margin-top: 4px; color: #6b7280; font-size: 13px }
.layout__page-actions { display: flex; align-items: center }
.layout__card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 8px 24px rgba(16,24,40,0.06); }
.layout__card-header { padding: 12px 16px; border-bottom: 1px solid #e5e7eb }
.layout__card-title { font-size: 14px; font-weight: 600 }
.layout__card-body { padding: 16px }
.layout__grid { display: grid; gap: 16px }
.layout__grid--2 { grid-template-columns: 1fr 1fr }
.btn--primary { background: #2563eb; color: #fff; border-color: #2563eb }
.btn--primary:disabled { opacity: 0.6; cursor: not-allowed }
.u-text-error { color: #dc2626 }
.u-text-green-600 { color: #16a34a }
.u-text-gray-600 { color: #4b5563 }
</style>
