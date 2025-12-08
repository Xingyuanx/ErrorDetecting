<template>
  <section class="layout__section">
    <div class="layout__page-header"><h2 class="layout__page-title">用户管理</h2></div>
    <div class="u-mb-2"><button class="btn" @click="open=true">新增用户</button></div>
    <table id="admin-user-table" class="dashboard__table"><thead><tr><th>用户名</th><th>邮箱</th><th>角色</th><th>状态</th><th>操作</th></tr></thead><tbody><tr v-for="u in users" :key="u.username" class="dashboard__table-row"><td>{{ u.username }}</td><td>{{ u.email }}</td><td>{{ roleName(u.role) }}</td><td>{{ statusName(u.status) }}</td><td><button class="btn u-text-sm" @click="ban(u.username)">封禁</button><button class="btn u-text-sm u-ml-1" @click="unban(u.username)">解禁</button><button class="btn u-text-sm u-ml-1" @click="del(u.username)">删除</button></td></tr></tbody></table>
    <div v-show="open" class="u-mt-2">
      <form @submit.prevent="save">
        <input v-model.trim="form.username" placeholder="用户名" class="header__search-input" />
        <input v-model.trim="form.email" placeholder="邮箱" class="header__search-input" />
        <select v-model="form.role" class="header__search-input"><option value="admin">管理员</option><option value="operator">操作员</option><option value="observer">观察员</option></select>
        <select v-model="form.status" class="header__search-input"><option value="enabled">启用</option><option value="pending">待审核</option><option value="disabled">禁用</option></select>
        <button class="btn">保存</button>
        <button class="btn u-ml-1" type="button" @click="cancel">取消</button>
      </form>
      <div class="u-text-sm u-text-gray-700">{{ err }}</div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import api from '../lib/api'
const auth = useAuthStore()
const users = reactive<{ username:string; email:string; role:string; status:string }[]>([])
const open = ref(false)
const err = ref('')
const form = reactive({ username:'', email:'', role:'operator', status:'enabled' })
function roleName(r:string){ if(r==='admin')return '管理员'; if(r==='operator')return '操作员'; if(r==='observer')return '观察员'; return r }
function statusName(s:string){ if(s==='enabled')return '启用'; if(s==='pending')return '待审核'; if(s==='disabled')return '禁用'; return s }
async function load(){ try{ const r = await api.get('/v1/users',{ headers: auth.token?{ Authorization:`Bearer ${auth.token}` }:undefined }); users.splice(0,users.length,...(r.data?.users||[])) } catch(e:any){ err.value = e?.response?.data?.detail || '加载失败' } }
async function save(){ if(!form.username||!form.email||!form.role||!form.status){ err.value='请填写完整信息'; return } try{ await api.post('/v1/users', { ...form }, { headers: auth.token?{ Authorization:`Bearer ${auth.token}` }:undefined }); await load(); cancel() } catch(e:any){ const d=e?.response?.data; const errs=d?.detail?.errors; if(Array.isArray(errs)&&errs.length){ err.value = errs.map((x:any)=>x?.message||'').filter(Boolean).join('；') } else { err.value = d?.detail || '保存失败' } } }
function cancel(){ open.value=false; err.value=''; form.username=''; form.email=''; form.role='operator'; form.status='enabled' }
async function ban(u:string){ try{ await api.patch(`/v1/users/${encodeURIComponent(u)}`, { status:'disabled' }, { headers: auth.token?{ Authorization:`Bearer ${auth.token}` }:undefined }); await load() } catch(e:any){ err.value = e?.response?.data?.detail || '操作失败' } }
async function unban(u:string){ try{ await api.patch(`/v1/users/${encodeURIComponent(u)}`, { status:'enabled' }, { headers: auth.token?{ Authorization:`Bearer ${auth.token}` }:undefined }); await load() } catch(e:any){ err.value = e?.response?.data?.detail || '操作失败' } }
async function del(u:string){ try{ await api.delete(`/v1/users/${encodeURIComponent(u)}`, { headers: auth.token?{ Authorization:`Bearer ${auth.token}` }:undefined }); await load() } catch(e:any){ err.value = e?.response?.data?.detail || '删除失败' } }
onMounted(()=>{ load() })
</script>
