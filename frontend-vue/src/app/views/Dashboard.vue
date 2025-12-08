<template>
  <section class="layout__section">
    <div class="layout__page-header">
      <h2 class="layout__page-title">仪表板 · 集群概览</h2>
      <div class="top-meta">
        <span>更新时间：{{ updateTime }}</span>
        <span>当前集群：{{ meta.uuid }} | 主机名：{{ meta.host }} | 主IP：{{ meta.ip }}</span>
      </div>
    </div>
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-card-title">总节点数</div>
        <div class="stat-card-value">{{ totalCount }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-card-title">健康节点</div>
        <div class="stat-card-value text-success">{{ healthyCount }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-card-title">警告节点</div>
        <div class="stat-card-value text-warning">{{ warningCount }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-card-title">异常节点</div>
        <div class="stat-card-value text-error">{{ errorCount }}</div>
      </div>
    </div>
    <div class="grid grid-cols-2 gap-4">
      <div><CpuChart :cluster="meta.uuid" /></div>
      <div><MemoryChart :cluster="meta.uuid" /></div>
    </div>
    <article class="layout__card u-mt-4">
      <div class="layout__card-header">
        <h3 class="layout__card-title">节点状态详情</h3>
      </div>
      <div class="layout__card-body u-p-0">
        <div class="u-overflow-x-auto">
          <table class="dashboard__table" role="table">
            <thead class="dashboard__table-head">
              <tr>
                <th class="dashboard__table-th" scope="col">节点名称</th>
                <th class="dashboard__table-th" scope="col">IP 地址</th>
                <th class="dashboard__table-th" scope="col">状态</th>
                <th class="dashboard__table-th" scope="col">CPU 使用率</th>
                <th class="dashboard__table-th" scope="col">内存使用</th>
                <th class="dashboard__table-th" scope="col">最近更新</th>
                <th class="dashboard__table-th" scope="col">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr class="dashboard__table-row" v-for="n in nodes" :key="n.name">
                <td class="dashboard__table-td"><strong>{{ n.name }}</strong></td>
                <td class="dashboard__table-td">{{ n.ip }}</td>
                <td class="dashboard__table-td">
                  <span class="status-indicator">
                    <span :class="['status-dot', statusDotClass(n.status)]"></span>
                    <span class="status-text">{{ statusText(n.status) }}</span>
                  </span>
                </td>
                <td class="dashboard__table-td">{{ n.cpu }}</td>
                <td class="dashboard__table-td">{{ n.mem }}</td>
                <td class="dashboard__table-td">{{ n.updated }}</td>
                <td class="dashboard__table-td">
                  <button class="btn u-text-sm" @click="start(n.name)" data-requires-edit="true">启动</button>
                  <button class="btn u-text-sm u-ml-1" @click="stop(n.name)" data-requires-edit="true">停止</button>
                  <button class="btn u-text-sm u-ml-1" @click="remove(n.name)" data-requires-edit="true">删除</button>
                  <button class="btn u-text-sm u-ml-1" @click="detail(n.name)" data-requires-edit="true">详情</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </article>
</section>
</template>

<script setup lang="ts">
import { onMounted, reactive, computed } from 'vue'
import api from '../lib/api'
import { useAuthStore } from '../stores/auth'
import CpuChart from '../components/CpuChart.vue'
import MemoryChart from '../components/MemoryChart.vue'
const meta = reactive({ uuid: '未选择', host: '-', ip: '-' })
const auth = useAuthStore()
const nodes = reactive<Array<{ name:string; ip:string; status:'running'|'warning'|'error'; cpu:string; mem:string; updated:string }>>([])
const updateTime = computed(() => {
  const d = new Date()
  const y = d.getFullYear()
  const m = d.getMonth()+1
  const day = d.getDate()
  return `${y}年${m}月${day}日`
})
const totalCount = computed(() => nodes.length)
const healthyCount = computed(() => nodes.filter(n => n.status==='running').length)
const warningCount = computed(() => nodes.filter(n => n.status==='warning').length)
const errorCount = computed(() => nodes.filter(n => n.status==='error').length)
onMounted(() => {
  const raw = sessionStorage.getItem('current_cluster')
  if (raw) Object.assign(meta, JSON.parse(raw))
  loadNodes()
})
async function loadNodes(){
  try{
    const r = await api.get('/v1/nodes', { params: { cluster: meta.uuid }, headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
    const list = Array.isArray(r.data?.nodes) ? r.data.nodes : []
    nodes.splice(0, nodes.length, ...list.map((x:any)=>({ name:x.name, ip:x.ip, status:x.status, cpu:x.cpu, mem:x.mem, updated:x.updated })))
  }catch(e:any){ /* silent */ }
}
function statusText(s:'running'|'warning'|'error'){ return s==='running'?'运行中':s==='warning'?'警告':'异常' }
function statusDotClass(s:'running'|'warning'|'error'){ return s==='running'?'status-dot--running':s==='warning'?'status-dot--warning':'status-dot--error' }
async function start(name:string){ try{ await api.post(`/v1/nodes/${encodeURIComponent(name)}/start`, {}, { headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined }); await loadNodes() }catch(e:any){} }
async function stop(name:string){ try{ await api.post(`/v1/nodes/${encodeURIComponent(name)}/stop`, {}, { headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined }); await loadNodes() }catch(e:any){} }
async function remove(name:string){ try{ await api.delete(`/v1/nodes/${encodeURIComponent(name)}`, { headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined }); await loadNodes() }catch(e:any){} }
async function detail(name:string){ try{ await api.get(`/v1/nodes/${encodeURIComponent(name)}`, { headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined }) }catch(e:any){} }
</script>

<style scoped>
.top-meta{ display:flex; gap:16px; align-items:center; color:#6b7280; font-size:13px }
.ws-off{ color:#dc2626 }
.stats-grid{ display:grid; grid-template-columns: repeat(4, 1fr); gap:16px; margin:16px 0 }
.stat-card{ background:#ffffff; border:1px solid #e5e7eb; border-radius:12px; box-shadow:0 8px 24px rgba(16,24,40,0.06); padding:16px }
.stat-card-title{ color:#6b7280; font-size:13px }
.stat-card-value{ font-size:24px; font-weight:700 }
.text-success{ color:#16a34a }
.text-warning{ color:#f59e0b }
.text-error{ color:#dc2626 }
.status-indicator{ display:inline-flex; align-items:center; gap:6px }
.status-dot{ width:8px; height:8px; border-radius:50% }
.status-dot--running{ background:#16a34a }
.status-dot--warning{ background:#f59e0b }
.status-dot--error{ background:#dc2626 }
.status-text{ font-size:12px }
</style>
