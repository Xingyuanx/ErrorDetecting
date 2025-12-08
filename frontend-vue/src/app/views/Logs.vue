<template>
  <section class="layout__section">
    <div class="layout__page-header"><h2 class="layout__page-title">日志查询</h2></div>
    <form id="log-search-form" @submit.prevent="apply(true)">
      <select v-model="q.level" id="log-level" class="header__search-input">
        <option value="">全部级别</option>
        <option value="info">INFO</option>
        <option value="warn">WARN</option>
        <option value="error">ERROR</option>
      </select>
      <input v-model.trim="q.cluster" id="source-cluster" class="header__search-input" placeholder="集群" />
      <input v-model.trim="q.node" id="source-node" class="header__search-input" placeholder="节点" />
      <input v-model.trim="q.op" id="op-type" class="header__search-input" placeholder="操作类型" />
      <input v-model.trim="q.user" id="user-id" class="header__search-input" placeholder="用户" />
      <button class="btn">搜索</button>
      <button type="button" class="btn u-ml-1" @click="clear">清除筛选</button>
    </form>
    <div id="log-filter-summary" class="u-text-sm u-text-gray-700">当前筛选：无</div>
    <table class="dashboard__table">
      <thead><tr><th>时间</th><th>级别</th><th>集群</th><th>节点</th><th>操作</th><th>用户</th><th>消息</th></tr></thead>
      <tbody id="logs-tbody">
        <tr v-for="item in pageData" :key="item.id" class="dashboard__table-row">
          <td><time :datetime="item.time">{{ item.time.split('T')[1] || item.time }}</time></td>
          <td><span class="u-font-medium">{{ item.level.toUpperCase() }}</span></td>
          <td><code>{{ item.cluster }}</code></td>
          <td>{{ item.node }}</td>
          <td>{{ item.op }}</td>
          <td>{{ item.user }}</td>
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
import { computed, reactive, ref } from 'vue'
const data = ref<{ id:number; time:string; level:string; cluster:string; node:string; op:string; user:string; message:string }[]>([])
const page = ref(1)
const size = ref(10)
const q = reactive({ level:'', cluster:'', node:'', op:'', user:'' })
function seed() {
  const rows = [] as any[]
  for (let i=0;i<120;i++) rows.push({ id:i, time:`2025-01-01T0${i%10}:00:00`, level: ['info','warn','error'][i%3], cluster: ['CL-1111-AAAA','CL-2222-BBBB'][i%2], node: `node-${i%7}`, op: ['query','update','security'][i%3], user: ['alice','bob','carol'][i%3], message: `日志消息 ${i}` })
  data.value = rows
}
seed()
const filtered = computed(() => data.value.filter(item => (!q.level || item.level===q.level) && (!q.cluster||item.cluster===q.cluster) && (!q.node||item.node===q.node) && (!q.op||item.op===q.op) && (!q.user||item.user.toLowerCase().includes(q.user.toLowerCase()))))
const pageData = computed(() => filtered.value.slice((page.value-1)*size.value, (page.value)*size.value))
function apply(manual=false) { page.value = 1 }
function clear() { q.level=''; q.cluster=''; q.node=''; q.op=''; q.user=''; page.value=1 }
function prev() { if (page.value>1) page.value-=1 }
function next() { const max = Math.max(1, Math.ceil(filtered.value.length/size.value)); if (page.value<max) page.value+=1 }
</script>

