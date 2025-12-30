<template>
  <section class="layout__section">
    <div class="layout__page-header exec-header">
      <div>
        <h2 class="layout__page-title">执行日志</h2>
        <div class="layout__page-subtitle">查看与管理修复执行记录，支持完整后端同步</div>
      </div>
      <div class="header-actions">
        <button class="btn" type="button" @click="refresh">刷新</button>
        <button class="btn btn--primary u-ml-1" type="button" @click="openCreate=true">新增记录</button>
        <button class="btn u-ml-1" type="button" :disabled="!selected" @click="openEdit()">编辑记录</button>
        <button class="btn u-ml-1" type="button" :disabled="!selected" @click="delSelected()">删除记录</button>
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
            <input v-model.trim="form.id" placeholder="执行ID" class="header__search-input" />
            <input v-model.trim="form.faultId" placeholder="故障ID" class="header__search-input" />
            <select v-model="form.cmdType" class="header__search-input"><option>shell</option><option>hdfs</option><option>yarn</option></select>
            <select v-model="form.status" class="header__search-input"><option>running</option><option>success</option><option>failed</option></select>
            <input v-model.trim="form.start" placeholder="开始时间 如 2025-11-07 10:20:03" class="header__search-input" />
            <input v-model.trim="form.end" placeholder="结束时间 如 2025-11-07 10:22:35 或留空" class="header__search-input" />
            <input v-model.number="form.code" placeholder="退出码 如 0 或留空" class="header__search-input" />
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
type RecordItem = { id:string; faultId:string; cmdType:string; status:'running'|'success'|'failed'; start:string; end:string|''; code:number|null }
const auth = useAuthStore()
const records = reactive<RecordItem[]>([])
const selected = ref('')
const openCreate = ref(false)
const openEditForm = ref(false)
const err = ref('')
const loading = ref(false)
const form = reactive<RecordItem>({ id:'', faultId:'', cmdType:'shell', status:'running', start:'', end:'', code:null })

function select(r: RecordItem){ selected.value = r.id }
function editRow(r: RecordItem){ selected.value = r.id; openCreate.value=false; openEditForm.value=true; Object.assign(form, r) }
function openEdit(){ const r = records.find(x=>x.id===selected.value); if (r) editRow(r) }
function delSelected(){ if (selected.value) del(selected.value) }

async function del(id:string){
  try{
    await api.delete(`/v1/exec-logs/${encodeURIComponent(id)}`, { 
      headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined 
    })
    const i = records.findIndex(x=>x.id===id)
    if (i>=0) { 
      records.splice(i,1)
      if (selected.value===id) selected.value='' 
    }
  }catch(e:any){ 
    err.value = '删除失败：' + (e.response?.data?.detail || e.message || '网络错误')
  }
}

function cancelForm(){ openCreate.value=false; openEditForm.value=false; err.value='' }

async function save(){
  err.value=''
  if (!form.id || !form.faultId || !form.cmdType || !form.status || !form.start) { err.value='请完整填写信息'; return }
  const exists = records.find(x=>x.id===form.id)
  const payload = { 
    id: form.id, 
    faultId: form.faultId, 
    cmdType: form.cmdType, 
    status: form.status, 
    start: form.start, 
    end: form.end, 
    code: form.code 
  }
  
  try{
    if (openCreate.value) {
      if (exists) { err.value='执行ID已存在'; return }
      await api.post('/v1/exec-logs', {
        exec_id: payload.id,
        fault_id: payload.faultId,
        command_type: payload.cmdType,
        execution_status: payload.status,
        start_time: payload.start,
        end_time: payload.end || null,
        exit_code: payload.code
      }, { headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
    } else if (openEditForm.value) {
      if (!exists) { err.value='目标记录不存在'; return }
      await api.put(`/v1/exec-logs/${encodeURIComponent(form.id)}`, {
        fault_id: payload.faultId,
        command_type: payload.cmdType,
        execution_status: payload.status,
        start_time: payload.start,
        end_time: payload.end || null,
        exit_code: payload.code
      }, { headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
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
      id: d.exec_id || d.id,
      faultId: d.fault_id,
      cmdType: d.command_type || d.cmdType,
      status: d.execution_status || d.status,
      start: (d.start_time || d.start || '').replace('T',' ').slice(0,19),
      end: d.end_time ? String(d.end_time).replace('T',' ').slice(0,19) : '',
      code: d.exit_code ?? null
    }))
    records.splice(0, records.length, ...normalized)
  }catch(e:any){
    err.value = '加载执行日志失败：' + (e.response?.data?.detail || e.message || '网络错误')
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
