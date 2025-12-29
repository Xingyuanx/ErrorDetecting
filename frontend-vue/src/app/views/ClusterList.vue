<template>
  <!-- 页面：集群列表与注册
       职责：
       1）展示集群列表并提供操作入口
       2）提供“注册新集群”表单，完成校验与提交
       3）与仪表盘联动：持久化当前集群并跳转 -->
  <section class="layout__section">
    <div class="layout__page-header"><h2 class="layout__page-title">集群列表</h2></div>
    <div class="u-mb-2">
      <!-- 按钮：点击切换注册表单显隐（依赖 showRegister） -->
      <button class="btn" @click="toggleRegister">注册新集群</button>
    </div>
    <div v-show="showRegister" class="u-mb-2">
      <!-- 注册表单：分为“基本信息”和“节点详细配置”两部分 -->
      <form @submit.prevent="onRegister">
        <h4 class="u-text-gray-900 u-font-bold u-mb-1">1. 集群基本信息</h4>
        <div class="u-flex u-items-center u-mb-1">
          <!-- 集群名称；对应 DB 中的 name -->
          <input v-model.trim="name" placeholder="集群名称 (name)" class="header__search-input u-mr-1" />
          <!-- 集群类型；对应 DB 中的 type -->
          <select v-model="type" class="header__search-input u-mr-1">
            <option value="hadoop">Hadoop</option>
            <option value="spark">Spark</option>
            <option value="kubernetes">Kubernetes</option>
          </select>
          <!-- 节点总数；对应 DB 中的 node_count -->
          <input v-model.number="node_count" type="number" min="1" placeholder="节点总数 (node_count)" class="header__search-input u-mr-1" @input="onCountChange" />
          <!-- 健康状态；对应 DB 中的 health_status -->
          <select v-model="health_status" class="header__search-input">
            <option value="healthy">healthy</option>
            <option value="warning">warning</option>
            <option value="error">error</option>
            <option value="unknown">unknown</option>
          </select>
        </div>

        <div class="u-flex u-items-center u-mb-1">
          <!-- NameNode IP -->
          <input v-model.trim="namenode_ip" placeholder="NameNode IP" class="header__search-input u-mr-1" />
          <!-- NameNode 密码 -->
          <input v-model.trim="namenode_psw" type="password" placeholder="NameNode 密码" class="header__search-input u-mr-1" />
          <!-- ResourceManager IP -->
          <input v-model.trim="rm_ip" placeholder="RM IP" class="header__search-input u-mr-1" />
          <!-- ResourceManager 密码 -->
          <input v-model.trim="rm_psw" type="password" placeholder="RM 密码" class="header__search-input u-mr-1" />
          <!-- 集群描述 -->
          <input v-model.trim="description" placeholder="集群描述 (可选)" class="header__search-input" />
        </div>

        <h4 class="u-text-gray-900 u-font-bold u-mb-1 u-mt-2">2. 节点详细配置</h4>
        <!-- 节点列表：
             - 随 node_count 变化动态生成
             - 每项要求必填 hostname/ip_address/ssh_user/ssh_password -->
        <div v-for="(node, idx) in nodes" :key="idx" class="u-flex u-items-center u-mb-1">
          <span class="u-mr-1 u-text-sm u-text-gray-500">节点 {{ idx + 1 }}:</span>
          <!-- 节点主机名 -->
          <input v-model.trim="node.hostname" placeholder="节点主机名" class="header__search-input u-mr-1" />
          <!-- 节点 IP 地址；对应 DB 中的 ip_address -->
          <input v-model.trim="node.ip_address" placeholder="节点 IP (ip_address)" class="header__search-input u-mr-1" />
          <!-- SSH 用户名；对应 DB 中的 ssh_user -->
          <input v-model.trim="node.ssh_user" placeholder="SSH 用户 (ssh_user)" class="header__search-input u-mr-1" />
          <!-- SSH 密码；对应 DB 中的 ssh_password -->
          <input v-model.trim="node.ssh_password" type="password" placeholder="SSH 密码 (ssh_password)" class="header__search-input" />
        </div>

        <div class="u-mt-2">
          <button class="btn">提交注册</button>
          <button class="btn u-ml-1" type="button" @click="cancelRegister">取消</button>
        </div>
      </form>
      <div class="u-text-sm u-text-gray-700 u-mt-1">{{ err }}</div>
    </div>
    <div class="u-overflow-x-auto">
      <!-- 集群列表：
           - 点击行触发进入详情（@click）
           - 行内按钮使用 @click.stop 阻止冒泡，避免误导航 -->
      <table id="cluster-list-table" class="dashboard__table">
        <thead class="dashboard__table-head">
          <tr>
            <th class="dashboard__table-th">集群名</th>
            <th class="dashboard__table-th">节点数</th>
            <th class="dashboard__table-th">健康</th>
            <th class="dashboard__table-th">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in clusters" :key="c.uuid" class="dashboard__table-row" @click="toDashboard(c)">
            <td class="dashboard__table-td">{{ c.name }}</td>
            <td class="dashboard__table-td">{{ c.node_count }}</td>
            <td class="dashboard__table-td"><span>{{ c.healthText }}</span></td>
            <td class="dashboard__table-td">
              <button class="btn u-text-sm" @click.stop="toDashboard(c)">进入详情</button>
              <button class="btn u-text-sm u-ml-1" :disabled="c.health_status==='healthy'" @click.stop="startCluster(c.uuid)">启动集群</button>
              <button class="btn u-text-sm u-ml-1" :disabled="c.health_status!=='healthy'" @click.stop="stopCluster(c.uuid)">关闭集群</button>
              <button class="btn u-text-sm u-ml-1" @click.stop="unregister(c.uuid)">注销集群</button>
              <button class="btn u-text-sm u-ml-1" @click.stop="discover(c.uuid)">发现角色</button>
              <button class="btn u-text-sm u-ml-1" :disabled="c.health_status==='healthy'" @click.stop="startClusterNew(c.uuid)">按集群启动</button>
              <button class="btn u-text-sm u-ml-1" :disabled="c.health_status!=='healthy'" @click.stop="stopClusterNew(c.uuid)">按集群停止</button>
              <button class="btn u-text-sm u-ml-1" @click.stop="syncHosts(c.uuid)">同步 hosts</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup lang="ts">
// 视图脚本（Composition API / <script setup>）
// 职责：
// - 管理注册表单状态与校验
// - 执行后端交互（加载列表、注册、操作）
// - 与路由协作实现“进入详情”跳转
import { reactive, ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../lib/api'
import { useAuthStore } from '../stores/auth'
// 路由器实例；用于页面跳转（进入仪表盘）
const router = useRouter() // 页面跳转：进入仪表盘
// 认证 store；用于在请求头附加 Bearer token
const auth = useAuthStore() // 认证：在请求头附加 Bearer token
// 集群列表数据源；用于表格渲染（每行包含健康状态中文映射）
const clusters = reactive<{ uuid:string; name:string; node_count:number; health_status:string; healthText:string }[]>([]) // 列表数据源（用于表格渲染）
// 注册表单显隐状态；true 时显示注册表单
const showRegister = ref(false) // 注册表单显隐
// 注册表单：基础字段（对应 DB 中的 clusters 表结构）
const uuid = ref('') // 预留字段；通常由后端生成
const name = ref('') // 集群名称 (name)
const type = ref('hadoop') // 集群类型 (type)
const node_count = ref(1) // 节点总数 (node_count)
const health_status = ref('unknown') // 初始健康状态 (health_status)
const namenode_ip = ref('') // NameNode IP
const namenode_psw = ref('') // NameNode 密码
const rm_ip = ref('') // RM IP
const rm_psw = ref('') // RM 密码
const description = ref('') // 集群描述 (description)

// 节点列表：对应 DB 中的 nodes 表结构
// 使用 ref 而不是 reactive 来存储数组，避免响应式丢失问题
const nodes = ref<{hostname:string; ip_address:string; ssh_user:string; ssh_password:string}[]>([
  { hostname: '', ip_address: '', ssh_user: 'hadoop', ssh_password: '' }
])
// 错误提示区（中文）；显示在表单下方
const err = ref('') // 错误提示区（中文）

// 显隐切换：打开/关闭注册表单
function toggleRegister() { showRegister.value = !showRegister.value }

// 节点数量联动：
// 监听 node_count 变化以动态增删节点配置项
watch(node_count, (newVal) => {
  const target = Number(newVal) // 规范为 number
  if (!target || target < 1) return // 忽略无效值（小于 1）
  const current = nodes.value.length // 当前节点项数量
  if (target > current) {
    // 追加节点项至目标数量
    for (let i = current; i < target; i++) {
      nodes.value.push({ hostname: '', ip_address: '', ssh_user: 'hadoop', ssh_password: '' })
    }
  } else if (target < current) {
    // 截断数组，仅保留前 target 项
    nodes.value = nodes.value.slice(0, target)
  }
})

// 与模板兼容的空处理：保留 @input 钩子但逻辑由 watch 承担
function onCountChange() {} // Compatible with template

// 取消注册：重置所有表单字段与节点列表，关闭表单
function cancelRegister() {
  showRegister.value = false // 隐藏表单
  err.value = '' // 清空错误提示
  uuid.value = '' 
  name.value = ''
  type.value = 'hadoop'
  node_count.value = 1
  health_status.value = 'unknown'
  namenode_ip.value = ''
  namenode_psw.value = ''
  rm_ip.value = ''
  rm_psw.value = ''
  description.value = ''
  // 重置节点列表（恢复初始 1 项配置）
  nodes.value = [{ hostname: '', ip_address: '', ssh_user: 'hadoop', ssh_password: '' }]
}

// 健康状态中文映射
function healthTextOf(h:string){ return h==='healthy'?'健康':h==='warning'?'警告':h==='error'?'异常':'未知' }
// 错误格式化（中文）：
// - 兼容后端结构化错误 detail.errors（字段/步骤），拼接为多行提示
// - 针对常见 HTTP 状态码提供中文语义
// - 对网络不可达与常见前端运行时异常提供友好提示
function formatError(e: any, defaultMsg: string = '操作失败'): string {
  if (e?.response) {
    const s = e.response.status
    const d = e.response.data
    let detail = ''
    if (d?.detail) {
      if (typeof d.detail === 'string') detail = d.detail
      else if (Array.isArray(d.detail?.errors)) {
        // 格式化后端返回的详细错误列表
        detail = d.detail.errors.map((x:any) => {
          let msg = x?.message || '未知错误'
          if (x?.field) msg = `[${x.field}] ${msg}`
          if (x?.step) msg += ` (步骤: ${x.step})`
          return msg
        }).filter(Boolean).join('\n')
      }
    }
    
    // 常见状态码中文映射
    let prefix = ''
    switch(s) {
      case 400: prefix = '请求无效 (Bad Request)，请检查输入参数'; break
      case 401: prefix = '认证已过期，请重新登录'; break
      case 403: prefix = '权限受限，无法执行该操作'; break
      case 404: prefix = '未找到请求的资源 (Not Found)'; break
      case 409: prefix = '操作冲突，资源可能已存在'; break
      case 422: prefix = '输入验证失败，请核对数据格式'; break
      case 500: prefix = '服务器内部错误，请联系管理员或稍后重试'; break
      case 502: prefix = '网关错误，后端服务可能未启动'; break
      case 503: prefix = '服务暂时不可用，请稍后再试'; break
      case 504: prefix = '网关超时，后端响应过慢'; break
      default: prefix = `请求异常 (${s})`
    }
    
    return detail ? `${prefix}:\n${detail}` : prefix
  } else if (e?.request) {
    return '网络错误: 无法连接到服务器，请检查后端服务是否启动'
  }
  
  // 翻译常见的运行时错误
  const msg = e?.message || ''
  if (msg.includes('nodes.map is not a function')) {
    return '客户端错误: 节点列表数据格式异常 (nodes.map is not a function)，请尝试刷新页面'
  }
  
  return msg || defaultMsg
}

// 列表加载：
// 向后端 GET /api/v1/clusters 拉取集群列表，
// 使用 Authorization 头（若已登录），并映射为表格友好的展示结构
async function load(){
  try{
    // 拉取集群列表（实际请求路径为 /api/v1/clusters，因 api.baseURL='/api'）
    const r = await api.get('/v1/clusters', { headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
    // 保护性解析：若后端未返回数组则回退空数组
    const list = Array.isArray(r.data?.clusters) ? r.data.clusters : []
    // 映射为前端展示结构并附带中文健康文案
    clusters.splice(0, clusters.length, ...list.map((x:any)=>({ 
      uuid: x.uuid, 
      name: x.name || x.host || '', 
      node_count: Number(x.node_count || x.count) || 0, 
      health_status: x.health_status || x.health || 'unknown', 
      healthText: healthTextOf(x.health_status || x.health) 
    })))
  }catch(e:any){
    // 统一错误格式化输出至页面提示区
    err.value = formatError(e, '加载失败')
  }
}
// 注册提交：
// 流程：
// 1）必填校验（基本信息）
// 2）逐节点必填校验（hostname/ip_address/ssh_user/ssh_password）
// 3）构造 payload 并 POST /api/v1/clusters
// 4）成功后重置表单与刷新列表；失败时输出中文错误信息
async function onRegister() {
  // 1）基础必填校验
  if (!name.value || !node_count.value) { err.value = '请填写集群基本信息'; return }
  // 2）节点数组类型守护：确保为数组
  if (!Array.isArray(nodes.value)) {
    nodes.value = [{ hostname: '', ip_address: '', ssh_user: 'hadoop', ssh_password: '' }]
  }
  // 3）逐节点必填校验
  for (let i = 0; i < nodes.value.length; i++) {
    const n = nodes.value[i]
    if (!n.hostname || !n.ip_address || !n.ssh_user || !n.ssh_password) {
      err.value = `请完善第 ${i+1} 个节点的信息`
      return
    }
  }

  try{
    // 4）payload 构造：完全对应 DB 表结构字段
    const payload = {
      name: name.value,
      type: type.value,
      node_count: Number(node_count.value),
      health_status: health_status.value,
      namenode_ip: namenode_ip.value,
      namenode_psw: namenode_psw.value,
      rm_ip: rm_ip.value,
      rm_psw: rm_psw.value,
      description: description.value,
      nodes: nodes.value.map(n => ({
        hostname: n.hostname,
        ip_address: n.ip_address,
        ssh_user: n.ssh_user,
        ssh_password: n.ssh_password
      }))
    }
    // 5）提交注册
    await api.post('/v1/clusters', payload, { headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
    // 6）成功后：重置表单并刷新列表
    cancelRegister(); await load()
  }catch(e:any){
    // 7）失败处理
    err.value = formatError(e, '提交失败')
  }
}
// 注销集群：DELETE /api/v1/clusters/{id}，成功后刷新列表
async function unregister(id: string) {
  try{
    // 注销集群：DELETE /api/v1/clusters/{id}
    await api.delete(`/v1/clusters/${encodeURIComponent(id)}`, { headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
    await load()
  }
  catch(e:any){ err.value = formatError(e, '注销失败') }
}
// 启动（旧接口）：POST /api/v1/clusters/{id}/start
async function startCluster(id: string) {
  try{
    await api.post(`/v1/clusters/${encodeURIComponent(id)}/start`, {}, { headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
    await load()
  }
  catch(e:any){ err.value = formatError(e, '启动失败') }
}
// 停止（旧接口）：POST /api/v1/clusters/{id}/stop
async function stopCluster(id: string) {
  try{
    await api.post(`/v1/clusters/${encodeURIComponent(id)}/stop`, {}, { headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
    await load()
  }
  catch(e:any){ err.value = formatError(e, '关闭失败') }
}
// 进入详情（仪表盘）：
// 将当前集群写入 sessionStorage，供 Dashboard.vue 读取并展示
function toDashboard(c: any) {
  sessionStorage.setItem('current_cluster', JSON.stringify(c))
  router.push({ name: 'dashboard' })
}
onMounted(()=>{ load() })
// Hadoop 扩展接口：发现角色/按集群启动/按集群停止/同步 hosts
// 接口采用统一的返回结构（summary + warnings），失败时尽量拼接详细信息提升可读性
async function discover(id:string){
  try{
    const r = await api.post('/v1/hadoop/cluster/discover', {}, { params: { cluster: id }, headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
    const warnings: string[] = Array.isArray(r.data?.warnings) ? r.data.warnings : []
    err.value = (r.data?.summary || '') + (warnings.length? ' | '+warnings.join('；') : '')
  }catch(e:any){
    const d = e?.response?.data; const w = Array.isArray(d?.warnings)? d.warnings : []
    err.value = (d?.summary || d?.detail || '发现失败') + (w.length? ' | '+w.join('；') : '')
  }
}
async function startClusterNew(id:string){
  try{
    const r = await api.post('/v1/hadoop/cluster/start', {}, { params: { cluster: id }, headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
    const warnings: string[] = Array.isArray(r.data?.warnings) ? r.data.warnings : []
    err.value = (r.data?.summary || '启动完成') + (warnings.length? ' | '+warnings.join('；') : '')
  }catch(e:any){
    const d = e?.response?.data; const w = Array.isArray(d?.warnings)? d.warnings : []
    err.value = (d?.summary || d?.detail || '启动失败') + (w.length? ' | '+w.join('；') : '')
  } finally { await load() }
}
async function stopClusterNew(id:string){
  try{
    const r = await api.post('/v1/hadoop/cluster/stop', {}, { params: { cluster: id }, headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
    const warnings: string[] = Array.isArray(r.data?.warnings) ? r.data.warnings : []
    err.value = (r.data?.summary || '停止完成') + (warnings.length? ' | '+warnings.join('；') : '')
  }catch(e:any){
    const d = e?.response?.data; const w = Array.isArray(d?.warnings)? d.warnings : []
    err.value = (d?.summary || d?.detail || '停止失败') + (w.length? ' | '+w.join('；') : '')
  } finally { await load() }
}
async function syncHosts(id:string){
  try{
    const r = await api.post('/v1/hadoop/cluster/sync-hosts', {}, { params: { cluster: id }, headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
    const warnings: string[] = Array.isArray(r.data?.warnings) ? r.data.warnings : []
    err.value = (r.data?.summary || '同步完成') + (warnings.length? ' | '+warnings.join('；') : '')
  }catch(e:any){
    const d = e?.response?.data; const w = Array.isArray(d?.warnings)? d.warnings : []
    err.value = (d?.summary || d?.detail || '同步失败') + (w.length? ' | '+w.join('；') : '')
  }
}
</script>
