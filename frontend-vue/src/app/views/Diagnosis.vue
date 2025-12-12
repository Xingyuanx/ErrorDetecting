<template>
  <section class="layout__section">
    <div class="layout__page-header diag-header">
      <div class="diag-title">
        <h2 class="layout__page-title">故障诊断</h2>
        <span class="badge">原型</span>
      </div>
      <div class="diag-tools">
        <input class="header__search-input" v-model.trim="kw" placeholder="搜索节点或集群" />
      </div>
    </div>
    <div class="diag-layout">
      <aside class="diag-sidebar">
        <div class="diag-group" v-for="g in filteredGroups" :key="g.id">
          <button class="diag-group-toggle" type="button" @click="g.open=!g.open">
            <span :class="['chev', g.open?'chev--down':'chev--right']"></span>
            {{ g.name }}
          </button>
          <ul v-show="g.open" class="diag-node-list">
            <li v-for="n in g.nodes" :key="n" :class="['diag-node-item', selectedNode===n?'diag-node-item--active':'']" @click="selectNode(n)">
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
            <div class="fault-row"><span class="fault-key">故障代码</span><span class="fault-val">FLT-20251107-0001</span></div>
            <div class="fault-row"><span class="fault-key">发生时间</span><span class="fault-val">2025-11-07 10:15:00</span></div>
            <div class="fault-row"><span class="fault-key">影响范围</span><span class="fault-val">CL-3333-CCCC-003</span></div>
          </div>
        </article>
      </aside>

      <main class="diag-preview">
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
      </main>

      <aside class="diag-assistant">
        <article class="layout__card">
          <div class="layout__card-body">
            <div class="assist-row">
              <div class="assist-field">
                <label class="u-text-sm u-font-medium u-text-gray-700">智能体</label>
                <select v-model="agent" class="u-w-full u-p-2 u-border u-rounded u-mt-1">
                  <option value="诊断智能体">诊断智能体</option>
                </select>
              </div>
              <div class="assist-field">
                <label class="u-text-sm u-font-medium u-text-gray-700">模型</label>
                <select v-model="model" class="u-w-full u-p-2 u-border u-rounded u-mt-1">
                  <option value="gpt-4o-mini">gpt-4o-mini</option>
                </select>
              </div>
            </div>
          </div>
        </article>
        <article class="layout__card u-mt-2">
          <div class="layout__card-header"><h3 class="layout__card-title">对话历史</h3></div>
          <div class="layout__card-body">
            <div class="chat-history">
              <div class="chat-item">
                <div class="chat-role">系统</div>
                <div class="chat-text">欢迎使用多智能体诊断面板</div>
              </div>
              <div class="chat-item">
                <div class="chat-role">诊断智能体</div>
                <div class="chat-text">请在左侧选择节点并拖入关键日志作为上下文</div>
              </div>
            </div>
            <textarea class="chat-input" placeholder="支持Markdown输入..."></textarea>
            <div class="chat-actions">
              <button type="button" class="btn btn--primary">发送</button>
              <button type="button" class="btn btn--primary u-ml-1">生成状态报告</button>
            </div>
            <div class="chat-progress">
              <span>流式显示占位：</span>
              <div class="progress-bar"><div class="progress-fill" style="width:0%"></div></div>
            </div>
          </div>
        </article>
      </aside>
    </div>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
const kw = ref('')
const tab = ref<'live'|'auto'>('live')
const agent = ref('诊断智能体')
const model = ref('gpt-4o-mini')
const groups = reactive<Array<{ id:string; name:string; open:boolean; nodes:string[] }>>([
  { id:'cl-1111', name:'CL-1111-AAAA', open:true, nodes:['CL-1111-AAAA-001','CL-1111-AAAA-002','CL-1111-AAAA-003'] },
  { id:'cl-2222', name:'CL-2222-BBBB', open:true, nodes:['CL-2222-BBBB-001'] },
  { id:'cl-3333', name:'CL-3333-CCCC', open:true, nodes:['CL-3333-CCCC-003'] },
])
const selectedNode = ref('')
const filteredGroups = computed(()=>{
  const k = kw.value.trim().toLowerCase()
  if (!k) return groups
  return groups.map(g=>({ ...g, nodes: g.nodes.filter(n => n.toLowerCase().includes(k) || g.name.toLowerCase().includes(k)) }))
})
function selectNode(n:string){ selectedNode.value = n }
function statusDot(n:string){ return n.includes('003') ? 'status-dot--error' : n.includes('002') ? 'status-dot--warning' : 'status-dot--running' }
const previewLogs = computed(() => {
  if (!selectedNode.value) return [] as Array<{id:number;time:string;level:string;source:string;message:string}>
  return [
    { id:1, time:'2025-11-07T10:15:00', level:'error', source:selectedNode.value, message:'连接断开，心跳丢失' },
    { id:2, time:'2025-11-07T10:14:58', level:'warn', source:selectedNode.value, message:'心跳延迟超过阈值' },
    { id:3, time:'2025-11-07T10:14:55', level:'info', source:selectedNode.value, message:'尝试重连中' }
  ]
})
</script>

<style scoped>
.diag-header{ display:flex; align-items:center; justify-content:space-between }
.diag-title{ display:flex; align-items:center; gap:8px }
.badge{ padding:2px 8px; border-radius:999px; background:#eef2ff; color:#374151; font-size:12px }
.diag-layout{ display:grid; grid-template-columns: 320px 1fr 380px; gap:16px }
.diag-sidebar{ background:#ffffff; border:1px solid #e5e7eb; border-radius:12px; padding:12px; display:flex; flex-direction:column }
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
.status-dot--warning{ background:#f59e0b }
.status-dot--error{ background:#dc2626 }
.diag-tabs{ display:flex; gap:8px; margin-top:12px }
.diag-tip{ margin-top:8px; color:#6b7280; font-size:12px }
.fault-row{ display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px dashed #e5e7eb }
.fault-row:last-child{ border-bottom:none }
.fault-key{ color:#6b7280; font-size:12px }
.fault-val{ font-weight:600 }

.diag-preview{ display:flex }
.preview-meta{ color:#6b7280; font-size:12px }
.preview-placeholder{ color:#6b7280; font-size:14px }
.preview-body{ height:677.6px; background:#f9fafb; border:1px solid #e5e7eb; border-radius:8px; margin-top:8px }

.diag-assistant{ display:flex; flex-direction:column }
.assist-row{ display:grid; grid-template-columns: 1fr 1fr; gap:12px }
.assist-field{ display:flex; flex-direction:column }
.chat-history{ display:flex; flex-direction:column; gap:8px }
.chat-item{ display:flex; gap:8px }
.chat-role{ width:72px; color:#6b7280 }
.chat-text{ flex:1 }
.chat-input{ width:100%; min-height:80px; margin-top:8px; padding:8px; border:1px solid #e5e7eb; border-radius:8px }
.chat-actions{ display:flex; justify-content:flex-end; gap:8px; margin-top:8px }
.chat-progress{ display:flex; align-items:center; gap:8px; margin-top:8px; color:#6b7280 }
.progress-bar{ flex:1; height:6px; background:#e5e7eb; border-radius:999px; overflow:hidden }
.progress-fill{ height:100%; background:#2563eb }
</style>
