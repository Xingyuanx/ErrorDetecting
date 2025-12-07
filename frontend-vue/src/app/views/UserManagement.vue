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
import { reactive, ref } from 'vue'
const users = reactive<{ username:string; email:string; role:string; status:string }[]>([
  { username: 'alice', email: 'alice@example.com', role: 'admin', status: 'enabled' },
  { username: 'bob', email: 'bob@example.com', role: 'observer', status: 'pending' }
])
const open = ref(false)
const err = ref('')
const form = reactive({ username:'', email:'', role:'operator', status:'enabled' })
function roleName(r:string){ if(r==='admin')return '管理员'; if(r==='operator')return '操作员'; if(r==='observer')return '观察员'; return r }
function statusName(s:string){ if(s==='enabled')return '启用'; if(s==='pending')return '待审核'; if(s==='disabled')return '禁用'; return s }
function save(){ if(!form.username||!form.email||!form.role||!form.status){ err.value='请填写完整信息'; return } if(users.some(u=>u.username===form.username)){ err.value='用户名已存在'; return } users.push({ ...form }); cancel() }
function cancel(){ open.value=false; err.value=''; form.username=''; form.email=''; form.role='operator'; form.status='enabled' }
function ban(u:string){ const i=users.findIndex(x=>x.username===u); if(i>=0) users[i].status='disabled' }
function unban(u:string){ const i=users.findIndex(x=>x.username===u); if(i>=0) users[i].status='enabled' }
function del(u:string){ const i=users.findIndex(x=>x.username===u); if(i>=0) users.splice(i,1) }
</script>

