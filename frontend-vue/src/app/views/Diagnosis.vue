<template>
  <section class="layout__section">
    <div class="layout__page-header diag-header">
      <div class="diag-title">
        <h2 class="layout__page-title">故障诊断</h2>
      </div>
    </div>
    <div class="diag-layout">
      <aside class="diag-sidebar">
        <div class="diag-filter">
          <form class="diag-filter-grid">
            <div>
              <label class="u-text-sm u-font-medium u-text-gray-700">日志级别</label>
              <select v-model="filters.level" class="u-w-full u-p-2 u-border u-rounded u-mt-1">
                <option value="">全部级别</option>
                <option value="debug">DEBUG</option>
                <option value="info">INFO</option>
                <option value="warn">WARN</option>
                <option value="error">ERROR</option>
              </select>
            </div>
            <div>
              <label class="u-text-sm u-font-medium u-text-gray-700">来源集群</label>
              <select v-model="filters.cluster" class="u-w-full u-p-2 u-border u-rounded u-mt-1">
                <option value="">全部集群</option>
                <option v-for="c in clusterOptions" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
            <div>
              <label class="u-text-sm u-font-medium u-text-gray-700">来源节点</label>
              <select v-model="filters.node" class="u-w-full u-p-2 u-border u-rounded u-mt-1">
                <option value="">全部节点</option>
                <option v-for="n in nodesOptions" :key="n" :value="n">{{ n }}</option>
              </select>
            </div>
            <div>
              <label class="u-text-sm u-font-medium u-text-gray-700">时间范围</label>
              <select v-model="filters.timeRange" class="u-w-full u-p-2 u-border u-rounded u-mt-1">
                <option value="">全部时间</option>
                <option value="1h">最近1小时</option>
                <option value="6h">最近6小时</option>
                <option value="24h">最近24小时</option>
                <option value="7d">最近7天</option>
              </select>
            </div>
            <div class="filter-actions">
              <button type="button" class="btn btn-link" @click="clearFilters">清除筛选</button>
            </div>
          </form>
          <div class="u-text-sm u-text-gray-700 u-mt-2">{{ filterSummary }}</div>
        </div>
        <div class="diag-group" v-for="g in filteredGroups" :key="g.id">
          <button class="diag-group-toggle" type="button" @click="toggleGroup(g)">
            <span :class="['chev', g.open?'chev--down':'chev--right']"></span>
            {{ g.name }}
          </button>
          <ul v-show="g.open" class="diag-node-list">
            <li v-for="n in nodesForGroup(g)" :key="n" :class="['diag-node-item', selectedNode===n?'diag-node-item--active':'']" @click="selectNode(n)">
              <span class="status-dot" :class="statusDot(n)"></span>
              {{ n }}
            </li>
          </ul>
        </div>
        <div class="diag-tabs">
          <button :class="['btn', tab==='live'?'btn--primary':'']" type="button" @click="tab='live'">实时日志</button>
          <button :class="['btn', tab==='auto'?'btn--primary':'']" type="button" @click="tab='auto'">自动刷新中</button>
        </div>
        <div class="diag-tip">请选择集群或节点以显示相关日志</div>
        <article class="layout__card u-mt-2">
          <div class="layout__card-header"><h3 class="layout__card-title">故障信息</h3></div>
          <div class="layout__card-body">
            <div class="fault-row"><span class="fault-key">故障代码</span><span class="fault-val">{{ fault?.code || '—' }}</span></div>
            <div class="fault-row"><span class="fault-key">发生时间</span><span class="fault-val">{{ fault?.time || '—' }}</span></div>
            <div class="fault-row"><span class="fault-key">影响范围</span><span class="fault-val">{{ fault?.scope || '—' }}</span></div>
            <div class="u-text-sm u-text-error u-mt-1" v-if="faultErr">{{ faultErr }}</div>
          </div>
        </article>
      </aside>

      <aside class="diag-preview">
        <article class="layout__card">
          <div class="layout__card-header"><h3 class="layout__card-title">日志预览</h3></div>
          <div class="layout__card-body">
            <div v-if="!selectedNode" class="preview-placeholder">请选择左侧的集群或节点，预览日志内容</div>
            <div v-else>
              <div class="preview-meta">当前节点：<strong>{{ selectedNode }}</strong></div>
              <div class="u-overflow-x-auto u-mt-2">
                <table class="dashboard__table">
                  <thead><tr><th>时间</th><th>级别</th><th>来源</th><th>消息</th></tr></thead>
                  <tbody>
                    <tr class="dashboard__table-row" v-for="l in previewLogs" :key="l.id">
                      <td><time :datetime="l.time">{{ l.time.split('T')[1] || l.time }}</time></td>
                      <td class="u-font-medium">{{ l.level.toUpperCase() }}</td>
                      <td><code>{{ l.source }}</code></td>
                      <td>{{ l.message }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </article>
      </aside>

      <aside class="diag-assistant">
        <article class="layout__card">
          <div class="layout__card-body">
            <div class="assist-row u-mb-2">
              <div class="assist-field">
                <label class="u-text-sm u-font-medium u-text-gray-700">智能体</label>
                <select v-model="agent" class="u-w-full u-p-2 u-border u-rounded u-mt-1">
                  <option value="诊断智能体">诊断智能体</option>
                </select>
              </div>
              <div class="assist-field">
                <label class="u-text-sm u-font-medium u-text-gray-700">模型</label>
                <select v-model="model" class="u-w-full u-p-2 u-border u-rounded u-mt-1">
                  <option value="deepseek">deepseek</option>
                </select>
              </div>
            </div>
          </div>
          <div class="layout__card-header"><h3 class="layout__card-title">对话历史</h3></div>
          <div class="layout__card-body">
            <div class="chat-history" ref="chatHistory">
              <div class="chat-item" :class="m.role==='assistant'?'chat-item--assistant':m.role==='user'?'chat-item--user':''" v-for="(m, i) in visibleMessages" :key="'msg-'+i">
                <div class="chat-role">{{ roleLabel(m.role) }}</div>
                <div class="chat-text">
                  <div>{{ m.content }}</div>
                  <details v-if="m.reasoning" class="u-mt-1">
                    <summary>推理过程</summary>
                    <pre style="white-space: pre-wrap">{{ m.reasoning }}</pre>
                  </details>
                </div>
              </div>
            </div>
            <textarea class="chat-input" v-model.trim="inputMsg" placeholder="支持Markdown输入..."></textarea>
            <div class="chat-actions">
              <button type="button" class="btn btn--primary" :disabled="sending || !inputMsg" @click="send()">发送</button>
              <button type="button" class="btn btn--primary u-ml-1" :disabled="sending" @click="generateReport()">生成状态报告</button>
            </div>
            <div class="chat-progress">
              <span>{{ sending ? '正在生成回复...' : '就绪' }}</span>
              <div class="progress-bar"><div class="progress-fill" :style="{ width: sending ? '60%' : '0%' }"></div></div>
            </div>
            <div class="u-text-sm u-text-gray-700 u-mt-1">{{ err }}</div>
          </div>
        </article>
      </aside>
    </div>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref, computed, watch, onMounted, nextTick } from 'vue'
import api from '../lib/api'
import { useAuthStore } from '../stores/auth'
const kw = ref('')
const tab = ref<'live'|'auto'>('live')
const agent = ref('诊断智能体')
const model = ref('deepseek')
const filters = reactive<{ level:string; cluster:string; node:string; opType:string; sourceId:string; timeRange:string }>({ level:'', cluster:'', node:'', opType:'', sourceId:'', timeRange:'' })
type Group = { id:string; name:string; open:boolean; nodes:string[]; count?:number }
const groups = reactive<Group[]>([])
const loadingSidebar = ref(false)
type FaultInfo = { code:string; time:string; scope:string }
const fault = ref<FaultInfo|null>(null)
const faultErr = ref('')
const selectedNode = ref('')
const clusterOptions = computed(()=> groups.map(g=>g.name))
const nodesOptions = computed(()=>{
  if (filters.cluster) {
    const g = groups.find(x=>x.name===filters.cluster)
    return g ? g.nodes : []
  }
  return groups.flatMap(g=>g.nodes)
})
const filteredGroups = computed(()=>{
  const kraw = kw.value.trim().toLowerCase()
  let base = groups.filter(g => !filters.cluster || g.name === filters.cluster)
  if (kraw) {
    base = base.filter(g => g.name.toLowerCase().includes(kraw) || g.nodes.some(n => n.toLowerCase().includes(kraw)))
  }
  if (filters.node) {
    base = base.filter(g => g.nodes.includes(filters.node))
  }
  return base
})
function nodesForGroup(g:{ id:string; name:string; open:boolean; nodes:string[] }){
  const k = kw.value.trim().toLowerCase()
  let nodes = g.nodes
  if (k) nodes = nodes.filter(n => n.toLowerCase().includes(k) || g.name.toLowerCase().includes(k))
  if (filters.node) nodes = nodes.filter(n => n === filters.node)
  return nodes
}
function pad3(n:number){ return String(n).padStart(3,'0') }
async function loadClusters(){
  loadingSidebar.value = true
  try{
    const r = await api.get('/v1/clusters', { headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
    const list = Array.isArray(r.data?.clusters) ? r.data.clusters : []
    const mapped: Group[] = list.map((x:any)=>({
      id: String(x.uuid || x.id || x.host || x.name || ''),
      name: String(x.host || x.name || x.uuid || ''),
      open: false,
      nodes: [],
      count: Number(x.count)||0
    })).filter(g=>g.id && g.name)
    groups.splice(0, groups.length, ...mapped)
  }catch(e:any){
    // 保持现状并在提示区显示错误
    err.value = formatError(e, '集群列表加载失败')
  }finally{
    loadingSidebar.value = false
  }
}
async function loadNodesFor(clusterName:string){
  const g = groups.find(x=>x.name === clusterName)
  if (!g) return
  try{
    const r = await api.get('/v1/nodes', { params: { cluster: clusterName }, headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
    const nodes = Array.isArray(r.data?.nodes) ? r.data.nodes.map((x:any)=>String(x?.name||x)).filter(Boolean) : []
    if (nodes.length) g.nodes = nodes
    else if ((g.count||0) > 0) g.nodes = Array.from({length: g.count as number}, (_,i)=>`${clusterName}-${pad3(i+1)}`)
  }catch(e:any){
    if ((g.count||0) > 0 && g.nodes.length===0) g.nodes = Array.from({length: g.count as number}, (_,i)=>`${clusterName}-${pad3(i+1)}`)
    // 不打断交互，错误显示在提示区
    err.value = formatError(e, '节点列表加载失败')
  }
}
async function toggleGroup(g:Group){
  g.open = !g.open
  if (g.open && g.nodes.length===0) await loadNodesFor(g.name)
}
async function loadFaultInfo(){
  faultErr.value = ''
  fault.value = null
  const params:any = {}
  if (selectedNode.value) params.node = selectedNode.value
  else if (filters.cluster) params.cluster = filters.cluster
  try{
    const r = await api.get('/v1/faults/summary', { params, headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
    const d = r?.data?.fault || r?.data?.data || null
    if (d) fault.value = { code: String(d.code||''), time: String(d.time||''), scope: String(d.scope||'') }
  }catch(e:any){
    faultErr.value = formatError(e, '故障信息加载失败')
  }
}
function selectNode(n:string){ selectedNode.value = n }
function statusDot(n:string){ return n.includes('003') ? 'status-dot--error' : n.includes('002') ? 'status-dot--warning' : 'status-dot--running' }
const previewLogs = computed(() => {
  if (!selectedNode.value) return [] as Array<{id:number;time:string;level:string;source:string;message:string}>
  const list = [
    { id:1, time:'2025-11-07T10:15:00', level:'error', source:selectedNode.value, message:'连接断开，心跳丢失' },
    { id:2, time:'2025-11-07T10:14:58', level:'warn', source:selectedNode.value, message:'心跳延迟超过阈值' },
    { id:3, time:'2025-11-07T10:14:55', level:'info', source:selectedNode.value, message:'尝试重连中' }
  ]
  return filters.level ? list.filter(l => l.level === filters.level) : list
})
const auth = useAuthStore()
const messages = ref<Array<{ role: 'user'|'assistant'|'system'; content: string; reasoning?: string }>>([
  { role: 'system', content: '欢迎使用多智能体诊断面板' },
  { role: 'assistant', content: '请在左侧选择节点并拖入关键日志作为上下文' }
])
const visibleMessages = computed(() => messages.value.filter(m => m.role !== 'system'))
const chatHistory = ref<HTMLElement|null>(null)
function scrollToLatest(){ const el = chatHistory.value; if (el) el.scrollTop = el.scrollHeight }
const inputMsg = ref('')
const sending = ref(false)
const err = ref('')
function sessionIdOf(){ return selectedNode.value ? `diagnosis-${selectedNode.value}` : 'diagnosis-global' }
function roleLabel(r: string){ return r==='assistant' ? '诊断智能体' : r==='user' ? '我' : '系统' }
const filterSummary = computed(()=>{
  const items:string[] = []
  if (filters.level) items.push(`级别=${filters.level.toUpperCase()}`)
  if (filters.cluster) items.push(`集群=${filters.cluster}`)
  if (filters.node) items.push(`节点=${filters.node}`)
  if (filters.timeRange) items.push(`时间=${filters.timeRange}`)
  return items.length ? `当前筛选：${items.join('；')}` : '当前筛选：无'
})
function clearFilters(){ filters.level=''; filters.cluster=''; filters.node=''; filters.opType=''; filters.sourceId=''; filters.timeRange='' }
async function loadHistory(){
  err.value = ''
  try{
    const r = await api.get('/v1/ai/history', { params: { sessionId: sessionIdOf() }, headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
    const list = Array.isArray(r.data?.messages) ? r.data.messages : []
    messages.value = list.map((m:any)=>({ role: m.role || 'assistant', content: String(m.content || ''), reasoning: m.reasoning }))
    await nextTick()
    scrollToLatest()
  }catch(e:any){
    err.value = formatError(e, '历史记录加载失败')
  }
}
async function send(){
  if (!inputMsg.value) return
  sending.value = true
  err.value = ''
  const userMsg = { role: 'user' as const, content: inputMsg.value }
  messages.value.push(userMsg)
  try{
    const r = await api.post('/v1/ai/chat', { sessionId: sessionIdOf(), message: inputMsg.value, context: { node: selectedNode.value || '', agent: agent.value, model: model.value } }, { headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
    const reply = String(r.data?.reply || '')
    const reasoning = r.data?.reasoning
    messages.value.push({ role: 'assistant', content: reply, reasoning })
    await nextTick()
    scrollToLatest()
    inputMsg.value = ''
  }catch(e:any){
    err.value = formatError(e, '消息发送失败')
  }finally{
    sending.value = false
  }
}
async function generateReport(){
  inputMsg.value = inputMsg.value || `请根据当前节点${selectedNode.value || '（未选定）'}最近关键日志生成一份状态报告（包含症状、影响范围、根因假设与建议）。`
  await send()
}
onMounted(async ()=>{ await loadClusters(); await loadHistory(); await loadFaultInfo() })
watch(selectedNode, () => { loadHistory() })
watch(selectedNode, () => { loadFaultInfo() })
watch(() => filters.cluster, () => { loadFaultInfo() })
function formatError(e:any, def:string){
  const r = e?.response
  const s = r?.status
  const st = r?.statusText
  const d = r?.data
  const detail = typeof d?.detail === 'string' ? d.detail : ''
  const errs = Array.isArray(d?.detail?.errors) ? d.detail.errors : []
  const msgs: string[] = []
  if (s) msgs.push(`HTTP ${s}${st ? ' '+st : ''}`)
  if (detail) msgs.push(detail)
  if (errs.length) msgs.push(errs.map((x:any)=>x?.message||'').filter(Boolean).join('；'))
  if (!msgs.length) msgs.push(r ? def : '网络异常或后端不可用')
  if (s === 401) msgs.push('Token 已过期或未登录，请重新登录')
  return msgs.join(' | ')
}
</script>

<style scoped>
.diag-header{ display:flex; align-items:center; justify-content:space-between }
.diag-title{ display:flex; align-items:center; gap:8px }
.badge{ padding:2px 8px; border-radius:999px; background:#eef2ff; color:#374151; font-size:12px }
.diag-layout{ display:grid; grid-template-columns: var(--diag-sidebar-width, 30%) 1fr var(--diag-assistant-width, 30%); gap:16px; align-items: stretch }
.diag-sidebar{ background:#ffffff; border:1px solid #e5e7eb; border-radius:12px; padding:12px; display:flex; flex-direction:column; overflow-x:hidden }
.diag-filter{ padding-bottom:12px; border-bottom:1px solid #e5e7eb }
.diag-filter-grid{ display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin-top:8px }
.diag-filter-grid > div{ display:flex; flex-direction:column; min-width:0 }
.diag-filter-grid label{ margin-bottom:4px }
.diag-sidebar select{ width:100%; max-width:100%; box-sizing:border-box }
.filter-actions{ display:flex; justify-content:flex-end; margin-top:8px }
.diag-group{ margin-top:8px }
.diag-group-toggle{ width:100%; display:flex; align-items:center; gap:8px; padding:8px; border:1px solid #e5e7eb; border-radius:8px; background:#f9fafb; color:#374151 }
.chev{ width:0; height:0; border-style:solid }
.chev--right{ border-width:5px 0 5px 8px; border-color:transparent transparent transparent #6b7280 }
.chev--down{ border-width:8px 5px 0 5px; border-color:#6b7280 transparent transparent transparent }
.diag-node-list{ list-style:none; padding:8px 4px; margin:0 }
.diag-node-item{ display:flex; align-items:center; gap:8px; padding:6px 8px; border:1px solid #e5e7eb; border-radius:8px; background:#fff; margin-top:6px; cursor:pointer }
.diag-node-item:hover{ background:#f9fafb }
.diag-node-item--active{ background:#eef2ff; border-color:#c7d2fe }
.status-dot{ width:8px; height:8px; border-radius:50% }
.status-dot--running{ background:#16a34a }
.status-dot--warning{ background:#16a34a }
.status-dot--error{ background:#16a34a }
.diag-tabs{ display:flex; gap:8px; margin-top:12px }
.diag-tip{ margin-top:8px; color:#6b7280; font-size:12px }
.fault-row{ display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px dashed #e5e7eb }
.fault-row:last-child{ border-bottom:none }
.fault-key{ color:#6b7280; font-size:12px }
.fault-val{ font-weight:600 }

.diag-preview{ display:flex; flex-direction:column; height:100% }
.diag-preview .layout__card{ display:flex; flex-direction:column; height:100%; width:100% }
.diag-preview .layout__card-body{ flex:1; overflow:auto }
.preview-meta{ color:#6b7280; font-size:12px }
.preview-placeholder{ color:#6b7280; font-size:14px }
.preview-body{ background:#f9fafb; border:1px solid #e5e7eb; border-radius:8px; margin-top:8px; flex:1 }

.diag-assistant{ display:flex; flex-direction:column; margin-right: 16px }
.diag-assistant .layout__card{ display:flex; flex-direction:column; height:100% }
.diag-assistant .layout__card-body{ flex:1; overflow:auto }
.diag-assistant .layout__card-body:first-of-type{ flex:0; overflow:visible; padding-bottom:8px }
.diag-assistant .layout__card-body:last-of-type{ flex:1; overflow:auto }
.assist-row{ display:grid; grid-template-columns: 1fr 1fr; gap:12px }
.assist-field{ display:flex; flex-direction:column }
.chat-history{ display:flex; flex-direction:column; gap:8px; max-height: 360px; overflow-y: auto; overscroll-behavior: contain; padding-right: 4px }
.chat-item{ display:flex; gap:8px }
.chat-role{ width:72px; color:#6b7280 }
.chat-text{ flex:1; background:#f9fafb; border:1px solid #e5e7eb; border-radius:8px; padding:8px 10px; max-width:100%; overflow-x:hidden; word-break:break-word }
.chat-text *{ word-break:break-word; overflow-wrap:anywhere }
.chat-history{ overflow-x:hidden }
.chat-item--assistant .chat-text{ background:#f9fafb }
.chat-item--user .chat-text{ background:#eef2ff; border-color:#c7d2fe }
.chat-input{ width:100%; min-height:80px; margin-top:8px; padding:8px; border:1px solid #e5e7eb; border-radius:8px }
.chat-input:focus{ outline:none; border-color:#9ca3af; box-shadow:0 0 0 3px rgba(37,99,235,0.1) }
.chat-actions{ display:flex; justify-content:flex-end; gap:8px; margin-top:8px }
.chat-progress{ display:flex; align-items:center; gap:8px; margin-top:8px; color:#6b7280 }
.progress-bar{ flex:1; height:6px; background:#e5e7eb; border-radius:999px; overflow:hidden }
.progress-fill{ height:100%; background:#2563eb }

.layout__card{ background:#fff; border:1px solid #e5e7eb; border-radius:12px; box-shadow:0 8px 24px rgba(16,24,40,0.06) }
.layout__card-header{ padding:10px 12px; border-bottom:1px solid #e5e7eb }
.layout__card-title{ font-size:14px; font-weight:700 }
.layout__card-body{ padding:12px }
.diag-tabs .btn{ border-radius:999px; padding:6px 12px }
.diag-tabs .btn--primary{ background:#2563eb; border-color:#2563eb; color:#fff }
.diag-group-toggle{ transition: background 120ms ease, border-color 120ms ease }
.diag-group-toggle:hover{ background:#eef2ff; border-color:#c7d2fe }
</style>
