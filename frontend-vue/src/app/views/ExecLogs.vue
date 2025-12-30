<template>
  <section class="layout__section">
    <div class="layout__page-header exec-header">
      <div>
        <h2 class="layout__page-title">集群操作日志</h2>
        <div class="layout__page-subtitle">查看与管理修复执行记录，支持完整后端同步</div>
      </div>
      <div class="header-actions">
        <button class="btn" type="button" @click="refresh">刷新</button>
        <button class="btn btn--primary u-ml-1" type="button" @click="openCreate=true">新增记录</button>
        <button class="btn u-ml-1" type="button" :disabled="selected === null" @click="openEdit()">编辑记录</button>
        <button class="btn u-ml-1" type="button" :disabled="selected === null" @click="delSelected()">删除记录</button>
      </div>
    </div>

    <article class="layout__card">
      <div class="layout__card-header"><h3 class="layout__card-title">执行记录</h3></div>
      <div class="layout__card-body u-p-0">
        <ExecLogsTable :records="records" :selected-id="selected" @select="select" @edit="editRow" @delete="del" />
      </div>
    </article>

    <article class="layout__card u-mt-3" v-show="openCreate || openEditForm">
      <div class="layout__card-header"><h3 class="layout__card-title">{{ openCreate ? '新增记录' : '编辑记录' }}</h3></div>
      <div class="layout__card-body">
        <form @submit.prevent="save">
          <div class="form-grid">
            <input v-model.trim="form.clusterName" placeholder="集群名称" class="header__search-input" />
            <input v-model.trim="form.username" placeholder="用户" class="header__search-input" />
            <input v-model.trim="form.description" placeholder="描述" class="header__search-input" />
            <select v-model="form.status" class="header__search-input"><option>running</option><option>success</option><option>failed</option></select>
            <input v-model.trim="form.start" placeholder="开始时间 如 2025-11-07 10:20:03" class="header__search-input" />
            <input v-model.trim="form.end" placeholder="结束时间 如 2025-11-07 10:22:35 或留空" class="header__search-input" />
          </div>
          <div class="u-mt-2">
            <button class="btn btn--primary" type="submit">保存</button>
            <button class="btn u-ml-1" type="button" @click="cancelForm">取消</button>
          </div>
          <div class="u-text-sm u-text-error u-mt-1" v-if="err">{{ err }}</div>
        </form>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import api from '../lib/api'
import { useAuthStore } from '../stores/auth'
import ExecLogsTable from '../components/ExecLogsTable.vue'
type RecordItem = { id:number; clusterName:string; username:string; description:string; faultId:string; cmdType:string; status:'running'|'success'|'failed'; start:string; end:string|''; code:number|null }
const auth = useAuthStore()
const records = reactive<RecordItem[]>([])
const selected = ref<number|null>(null)
const openCreate = ref(false)
const openEditForm = ref(false)
const err = ref('')
const loading = ref(false)
const form = reactive<RecordItem>({ id:0, clusterName:'', username:'', description:'', faultId:'', cmdType:'shell', status:'running', start:'', end:'', code:null })

function select(r: RecordItem){ selected.value = r.id }
function editRow(r: RecordItem){ selected.value = r.id; openCreate.value=false; openEditForm.value=true; Object.assign(form, r) }
function openEdit(){ const r = records.find(x=>x.id===selected.value); if (r) editRow(r) }
function delSelected(){ if (selected.value !== null) del(selected.value) }

async function del(id:number){
  try{
    await api.delete(`/v1/exec-logs/${id}`, { 
      headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined 
    })
    const i = records.findIndex(x=>x.id===id)
    if (i>=0) { 
      records.splice(i,1)
      if (selected.value===id) selected.value=null 
    }
  }catch(e:any){ 
    err.value = '删除失败：' + (e.response?.data?.detail || e.message || '网络错误')
  }
}

function cancelForm(){ openCreate.value=false; openEditForm.value=false; err.value=''; Object.assign(form, { id:0, clusterName:'', username:'', description:'', faultId:'', cmdType:'shell', status:'running', start:'', end:'', code:null }) }

async function save(){
  err.value=''
  if (!form.clusterName || !form.start) { err.value='请完整填写信息'; return }
  
  const payload = { 
    from_user_id: auth.user?.id || 0,
    cluster_name: form.clusterName,
    description: form.description,
    fault_id: form.faultId, 
    command_type: form.cmdType, 
    execution_status: form.status, 
    start_time: form.start.replace(' ', 'T'), 
    end_time: form.end ? form.end.replace(' ', 'T') : null, 
    exit_code: form.code 
  }
  
  try{
    if (openCreate.value) {
      await api.post('/v1/exec-logs', payload, { headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
    } else if (openEditForm.value) {
      if (selected.value === null) { err.value='目标记录不存在'; return }
      await api.put(`/v1/exec-logs/${selected.value}`, payload, { headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
    }
    await load()
    cancelForm()
  }catch(e:any){ 
    err.value = '保存失败：' + (e.response?.data?.detail || e.message || '网络错误')
  }
}

async function refresh(){ await load() }

async function load(){
  loading.value = true
  err.value = ''
  try{
    const r = await api.get('/v1/exec-logs', { 
      headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined 
    })
    const items = Array.isArray(r.data?.items) ? r.data.items : (Array.isArray(r.data?.exec_logs) ? r.data.exec_logs : [])
    const normalized: RecordItem[] = items.map((d:any)=>({
      id: d.id,
      clusterName: d.cluster_name || '',
      username: d.username || d.user_name || d.user?.username || '',
      description: d.description || '',
      faultId: d.fault_id || '',
      cmdType: d.command_type || '',
      status: d.execution_status || 'running',
      start: (d.start_time || '').replace('T',' ').slice(0,19),
      end: d.end_time ? String(d.end_time).replace('T',' ').slice(0,19) : '',
      code: d.exit_code ?? null
    }))
    records.splice(0, records.length, ...normalized)
  }catch(e:any){
    err.value = '加载集群操作日志失败：' + (e.response?.data?.detail || e.message || '网络错误')
    records.splice(0, records.length)
  } finally { 
    loading.value = false 
  }
}

onMounted(()=>{ load() })
</script>

<style scoped>
.exec-header{ display:flex; justify-content:space-between; align-items:center }
.layout__page-subtitle{ color:#6b7280; font-size:13px }
.header-actions{ display:flex; align-items:center }
.row--selected{ background:#eef2ff }
.layout__card{ background:#ffffff; border:1px solid #e5e7eb; border-radius:12px; box-shadow:0 8px 24px rgba(16,24,40,0.06) }
.layout__card-header{ padding:12px 16px; border-bottom:1px solid #e5e7eb }
.layout__card-title{ font-size:14px; font-weight:600 }
.layout__card-body{ padding:16px }
.form-grid{ display:grid; grid-template-columns: repeat(4, 1fr); gap:12px }
.status--running{ color:#2563eb }
.status--success{ color:#16a34a }
.status--failed{ color:#dc2626 }
.u-text-error { color: #dc2626; }
</style>
