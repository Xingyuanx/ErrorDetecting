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
      <thead><tr><th>主机名</th><th>IP</th><th>节点数</th><th>健康</th><th>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;操作</th></tr></thead>
      <tbody>
        <tr v-for="c in clusters" :key="c.uuid" class="dashboard__table-row" @click="toDashboard(c)">
          <td>{{ c.host }}</td><td>{{ c.ip }}</td><td>{{ c.count }}</td>
          <td><span>{{ c.healthText }}</span></td>
          <td>
            <button class="btn u-text-sm" @click.stop="toDashboard(c)">进入详情</button>
            <button class="btn u-text-sm u-ml-1" @click.stop="startCluster(c.uuid)">启动集群</button>
            <button class="btn u-text-sm u-ml-1" @click.stop="stopCluster(c.uuid)">关闭集群</button>
            <button class="btn u-text-sm u-ml-1" @click.stop="unregister(c.uuid)">注销集群</button>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../lib/api'
import { useAuthStore } from '../stores/auth'
const router = useRouter()
const auth = useAuthStore()
const clusters = reactive<{ uuid:string; host:string; ip:string; count:number; health:string; healthText:string }[]>([])
const showRegister = ref(false)
const uuid = ref('')
const host = ref('')
const ip = ref('')
const count = ref('')
const health = ref('running')
const err = ref('')
function toggleRegister() { showRegister.value = !showRegister.value }
function cancelRegister() { showRegister.value = false; err.value = ''; uuid.value=''; host.value=''; ip.value=''; count.value=''; health.value='running' }
function healthTextOf(h:string){ return h==='running'?'健康':h==='warning'?'警告':'异常' }
async function load(){
  try{
    const r = await api.get('/v1/clusters', { headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
    const list = Array.isArray(r.data?.clusters) ? r.data.clusters : []
    clusters.splice(0, clusters.length, ...list.map((x:any)=>({ uuid:x.uuid, host:x.host, ip:x.ip, count:Number(x.count)||0, health:x.health, healthText: healthTextOf(x.health) })))
  }catch(e:any){ err.value = e?.response?.data?.detail || '加载失败' }
}
async function onRegister() {
  if (!uuid.value || !host.value || !ip.value || !count.value) { err.value = '请填写完整信息'; return }
  try{
    await api.post('/v1/clusters', { uuid: uuid.value, host: host.value, ip: ip.value, count: Number(count.value)||0, health: health.value }, { headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
    cancelRegister(); await load()
  }catch(e:any){
    const d = e?.response?.data; const errs = d?.detail?.errors
    if (Array.isArray(errs) && errs.length) err.value = errs.map((x:any)=>x?.message||'').filter(Boolean).join('；')
    else err.value = d?.detail || '提交失败'
  }
}
async function unregister(id: string) {
  try{ await api.delete(`/v1/clusters/${encodeURIComponent(id)}`, { headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined }); await load() }
  catch(e:any){ err.value = e?.response?.data?.detail || '注销失败' }
}
async function startCluster(id: string) {
  try{ await api.post(`/v1/clusters/${encodeURIComponent(id)}/start`, {}, { headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined }); await load() }
  catch(e:any){
    const d = e?.response?.data; const errs = d?.detail?.errors
    if (Array.isArray(errs) && errs.length) err.value = errs.map((x:any)=>x?.message||'').filter(Boolean).join('；')
    else err.value = d?.detail || '启动失败'
  }
}
async function stopCluster(id: string) {
  try{ await api.post(`/v1/clusters/${encodeURIComponent(id)}/stop`, {}, { headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined }); await load() }
  catch(e:any){
    const d = e?.response?.data; const errs = d?.detail?.errors
    if (Array.isArray(errs) && errs.length) err.value = errs.map((x:any)=>x?.message||'').filter(Boolean).join('；')
    else err.value = d?.detail || '关闭失败'
  }
}
function toDashboard(c: any) {
  sessionStorage.setItem('current_cluster', JSON.stringify(c))
  router.push({ name: 'dashboard' })
}
onMounted(()=>{ load() })
</script>
