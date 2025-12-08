<template>
  <section class="layout__section">
    <div class="layout__page-header"><h2 class="layout__page-title">日志查询</h2></div>
    <article class="layout__card">
      <div class="layout__card-header"><h3 class="layout__card-title">搜索条件</h3></div>
      <div class="layout__card-body">
        <form id="log-search-form" @submit.prevent="apply(true)" class="layout__grid layout__grid--3">
          <div>
            <label class="u-text-sm u-font-medium u-text-gray-700">日志级别</label>
            <select v-model="q.level" id="log-level" class="u-w-full u-p-2 u-border u-rounded u-mt-1">
              <option value="">全部级别</option>
              <option value="debug">DEBUG</option>
              <option value="info">INFO</option>
              <option value="warn">WARN</option>
              <option value="error">ERROR</option>
            </select>
          </div>
          <div>
            <label class="u-text-sm u-font-medium u-text-gray-700">来源集群</label>
            <select v-model="q.cluster" id="source-cluster" class="u-w-full u-p-2 u-border u-rounded u-mt-1">
              <option value="">全部集群</option>
              <option v-for="c in clustersOpts" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
          <div>
            <label class="u-text-sm u-font-medium u-text-gray-700">来源节点</label>
            <select v-model="q.node" id="source-node" class="u-w-full u-p-2 u-border u-rounded u-mt-1">
              <option value="">全部节点</option>
              <option v-for="n in nodesOpts" :key="n" :value="n">{{ n }}</option>
            </select>
          </div>
          <div>
            <label class="u-text-sm u-font-medium u-text-gray-700">操作类型</label>
            <select v-model="q.op" id="op-type" class="u-w-full u-p-2 u-border u-rounded u-mt-1">
              <option value="">全部类型</option>
              <option v-for="o in opsOpts" :key="o" :value="o">{{ o }}</option>
            </select>
          </div>
          <div>
            <label class="u-text-sm u-font-medium u-text-gray-700">来源：</label>
            <input v-model.trim="q.source" id="source-id" class="u-w-full u-p-2 u-border u-rounded u-mt-1" placeholder="如：alice、ops 等" />
          </div>
          <div>
            <label class="u-text-sm u-font-medium u-text-gray-700">时间范围</label>
            <select v-model="q.timeRange" id="time-range" class="u-w-full u-p-2 u-border u-rounded u-mt-1">
              <option value="">全部时间</option>
              <option value="1h">最近1小时</option>
              <option value="6h">最近6小时</option>
              <option value="24h">最近24小时</option>
              <option value="7d">最近7天</option>
            </select>
          </div>
          <div class="filter-actions" style="grid-column: 1 / -1;">
            <button type="button" class="btn btn-link" @click="clear">清除筛选</button>
          </div>
        </form>
        <div id="log-filter-summary" class="u-mt-3 u-text-sm u-text-gray-700">当前筛选：{{ summary }}</div>
      </div>
    </article>
    <table class="dashboard__table">
      <thead><tr><th>时间</th><th>级别</th><th>集群</th><th>节点</th><th>操作</th><th>来源</th><th>消息</th></tr></thead>
      <tbody id="logs-tbody">
        <tr v-for="item in pageData" :key="item.id" class="dashboard__table-row">
          <td><time :datetime="item.time">{{ item.time.split('T')[1] || item.time }}</time></td>
          <td><span class="u-font-medium">{{ item.level.toUpperCase() }}</span></td>
          <td><code>{{ item.cluster }}</code></td>
          <td>{{ item.node }}</td>
          <td>{{ item.op }}</td>
          <td>{{ item.source }}</td>
          <td>{{ item.message }}</td>
        </tr>
      </tbody>
    </table>
    <div class="u-mt-2">
      <button id="log-prev" class="btn" @click="prev">上一页</button>
      <button id="log-next" class="btn u-ml-1" @click="next">下一页</button>
      <select id="log-page-size" v-model.number="size" class="header__search-input u-ml-1"><option :value="10">10</option><option :value="20">20</option><option :value="50">50</option></select>
      <span id="log-page-info" class="u-ml-1">第 {{ page }} 页</span>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch, onMounted } from 'vue'
import api from '../lib/api'
import { useAuthStore } from '../stores/auth'
const auth = useAuthStore()
const data = ref<{ id:number; time:string; level:string; cluster:string; node:string; op:string; source:string; message:string }[]>([])
const page = ref(1)
const size = ref(10)
const total = ref(0)
const loading = ref(false)
const err = ref('')
const q = reactive({ level:'', cluster:'', node:'', op:'', source:'', timeRange:'' })
const clustersOpts = ref<string[]>([])
const nodesOpts = ref<string[]>([])
const opsOpts = ref<string[]>([])
function rangeFromNow(r:string){
  const now = Date.now()
  const span = r==='1h'?60*60*1000:r==='6h'?6*60*60*1000:r==='24h'?24*60*60*1000:r==='7d'?7*24*60*60*1000:0
  return span? new Date(now-span).toISOString() : ''
}
async function load(){
  loading.value = true
  err.value = ''
  try{
    const params: any = { page: page.value, size: size.value }
    if (q.level) params.level = q.level
    if (q.cluster) params.cluster = q.cluster
    if (q.node) params.node = q.node
    if (q.op) params.op = q.op
    if (q.source) params.source = q.source
    if (q.timeRange) params.time_from = rangeFromNow(q.timeRange)
    const r = await api.get('/v1/logs', { params, headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
    const items = Array.isArray(r.data?.items) ? r.data.items : (Array.isArray(r.data?.logs)? r.data.logs : [])
    const normalized = items.map((d:any)=>({ ...d, source: String((d?.source ?? d?.user ?? '') || '') }))
    data.value = normalized
    total.value = Number(r.data?.total ?? items.length)
    if (!clustersOpts.value.length) clustersOpts.value = Array.from(new Set(items.map((d:any)=>d.cluster).filter(Boolean)))
    if (!nodesOpts.value.length) nodesOpts.value = Array.from(new Set(items.map((d:any)=>d.node).filter(Boolean)))
    if (!opsOpts.value.length) opsOpts.value = Array.from(new Set(items.map((d:any)=>d.op).filter(Boolean)))
  }catch(e:any){ err.value = e?.response?.data?.detail || '加载失败' }
  finally{ loading.value = false }
}
function apply(manual=false) { page.value = 1 }
function clear() { q.level=''; q.cluster=''; q.node=''; q.op=''; q.source=''; q.timeRange=''; page.value=1 }
function prev() { if (page.value>1) { page.value-=1; load() } }
function next() { const max = Math.max(1, Math.ceil(total.value/size.value)); if (page.value<max) { page.value+=1; load() } }
const pageData = computed(() => {
  const s = q.source.trim().toLowerCase()
  let list = data.value
  if (s) list = list.filter(d => String(d.source || '').toLowerCase().includes(s))
  return list
})
watch(() => ({...q}), () => { apply(); load() }, { deep: true })
watch(size, () => { page.value = 1; load() })
onMounted(()=>{ load() })
const summary = computed(() => {
  const parts = [] as string[]
  if (q.level) parts.push(`级别=${q.level}`)
  if (q.cluster) parts.push(`集群=${q.cluster}`)
  if (q.node) parts.push(`节点=${q.node}`)
  if (q.op) parts.push(`类型=${q.op}`)
  if (q.source) parts.push(`来源=${q.source}`)
  if (q.timeRange) parts.push(`时间=${q.timeRange}`)
  return parts.length? parts.join('，') : '无'
})
</script>

<style scoped>
.layout__card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 8px 24px rgba(16,24,40,0.06) }
.layout__card-header { padding: 12px 16px; border-bottom: 1px solid #e5e7eb }
.layout__card-title { font-size: 14px; font-weight: 600 }
.layout__card-body { padding: 16px }
.layout__grid { display: grid; gap: 16px }
.layout__grid--3 { grid-template-columns: 1fr 1fr 1fr }
.btn--primary { background: #2563eb; color: #fff; border-color: #2563eb }
.btn--primary:disabled { opacity: 0.6; cursor: not-allowed }
.btn-link { background: transparent; border-color: transparent; color: #2563eb }
.filter-actions { display: flex; justify-content: flex-end; align-items: center; }
</style>
