<template>
  <section class="layout__section">
    <div class="layout__page-header"><h2 class="layout__page-title">集群列表</h2></div>
    <div class="u-mb-2">
      <button class="btn" @click="toggleRegister">注册新集群</button>
    </div>
    <div v-show="showRegister" class="u-mb-2">
      <form @submit.prevent="onRegister">
        <input v-model.trim="uuid" placeholder="UUID" class="header__search-input" />
        <input v-model.trim="host" placeholder="Master 主机名" class="header__search-input" />
        <input v-model.trim="ip" placeholder="Master IP" class="header__search-input" />
        <input v-model.trim="count" placeholder="节点数量" class="header__search-input" />
        <select v-model="health" class="header__search-input"><option value="running">健康</option><option value="warning">警告</option><option value="error">异常</option></select>
        <button class="btn">提交</button>
        <button class="btn u-ml-1" type="button" @click="cancelRegister">取消</button>
      </form>
      <div class="u-text-sm u-text-gray-700">{{ err }}</div>
    </div>
    <table id="cluster-list-table" class="dashboard__table">
      <thead><tr><th>UUID</th><th>主机名</th><th>IP</th><th>节点数</th><th>健康</th><th>操作</th></tr></thead>
      <tbody>
        <tr v-for="c in clusters" :key="c.uuid" class="dashboard__table-row" @click="toDashboard(c)">
          <td><code>{{ c.uuid }}</code></td><td>{{ c.host }}</td><td>{{ c.ip }}</td><td>{{ c.count }}</td>
          <td><span>{{ c.healthText }}</span></td>
          <td><button class="btn u-text-sm" @click.stop="unregister(c.uuid)">注销集群</button></td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
const clusters = reactive<{ uuid:string; host:string; ip:string; count:number; health:string; healthText:string }[]>([
  { uuid: 'CL-1111-AAAA', host: 'master-1', ip: '10.0.0.1', count: 8, health: 'running', healthText: '健康' },
  { uuid: 'CL-2222-BBBB', host: 'master-2', ip: '10.0.0.2', count: 12, health: 'warning', healthText: '警告' }
])
const showRegister = ref(false)
const uuid = ref('')
const host = ref('')
const ip = ref('')
const count = ref('')
const health = ref('running')
const err = ref('')
function toggleRegister() { showRegister.value = !showRegister.value }
function cancelRegister() { showRegister.value = false; err.value = ''; uuid.value=''; host.value=''; ip.value=''; count.value=''; health.value='running' }
function onRegister() {
  if (!uuid.value || !host.value || !ip.value || !count.value) { err.value = '请填写完整信息'; return }
  if (clusters.some(x => x.uuid === uuid.value)) { err.value = '该集群UUID已存在'; return }
  clusters.push({ uuid: uuid.value, host: host.value, ip: ip.value, count: Number(count.value)||0, health: health.value, healthText: health.value==='running'?'健康':health.value==='warning'?'警告':'异常' })
  cancelRegister()
}
function unregister(id: string) {
  const i = clusters.findIndex(x => x.uuid === id)
  if (i >= 0) clusters.splice(i, 1)
}
function toDashboard(c: any) {
  sessionStorage.setItem('current_cluster', JSON.stringify(c))
  router.push({ name: 'dashboard' })
}
</script>

