<template>
  <div class="dashboard-container">
    <div class="page-header">
      <div class="header-main">
        <h2 class="page-title">仪表板 · 集群概览</h2>
        <el-tag type="info" effect="plain" class="update-time">
          更新时间：{{ updateTime }}
        </el-tag>
        <el-tag v-if="isMonitoring" type="success" effect="dark" round class="status-tag">
          <el-icon class="is-loading" style="vertical-align: middle; margin-right: 4px;"><Loading /></el-icon>
          后台监控中 ({{ monitorInterval }}s)
        </el-tag>
      </div>
      <div class="cluster-info">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="集群 UUID">{{ meta.uuid }}</el-descriptions-item>
          <el-descriptions-item label="集群名称">{{ meta.name }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </div>

    <el-row :gutter="16" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="总节点数" :value="totalCount" />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="健康节点" :value="healthyCount" value-style="color: var(--el-color-success)" />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="警告节点" :value="warningCount" value-style="color: var(--el-color-warning)" />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="异常节点" :value="errorCount" value-style="color: var(--el-color-danger)" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="charts-row">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" header="CPU 使用率比例">
          <CpuChart :cluster="meta.uuid" />
        </el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" header="内存配额比例">
          <MemoryChart :cluster="meta.uuid" />
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" class="nodes-card">
      <template #header>
        <div class="card-header">
          <span>节点状态详情</span>
          <div class="header-actions">
            <template v-if="meta.uuid !== '未选择'">
              <el-button v-if="!isMonitoring" type="warning" link @click="collectMetrics" :loading="collecting || syncing">启动监控</el-button>
              <template v-else>
                <el-button type="danger" link @click="stopMonitoring" :loading="syncing">停止监控</el-button>
              </template>
              <el-button type="primary" link @click="loadNodes" :loading="syncing">刷新列表</el-button>
            </template>
          </div>
        </div>
      </template>
      <el-table :data="nodes" style="width: 100%" stripe>
        <el-table-column prop="name" label="节点名称" min-width="120">
          <template #default="{ row }">
            <span class="font-bold">{{ row.name }}</span>
            <el-tooltip v-if="row.error" :content="row.error" placement="top">
              <el-icon class="ml-1 text-red-500" style="vertical-align: middle; margin-left: 4px;"><CircleCloseFilled /></el-icon>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="ip" label="IP 地址" width="140" />
        <el-table-column prop="cpu" label="CPU 使用率" width="120" />
        <el-table-column prop="mem" label="内存使用率" width="120" />
        <el-table-column prop="updated" label="最近更新" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button type="primary" size="small" @click="start(row.name)">启动</el-button>
              <el-button type="warning" size="small" @click="stop(row.name)">停止</el-button>
              <el-popconfirm title="确定删除该节点吗？" @confirm="remove(row.name)">
                <template #reference>
                  <el-button type="danger" size="small">删除</el-button>
                </template>
              </el-popconfirm>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 采集进度弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="'正在启动采集: ' + meta.name"
      width="60%"
      class="log-dialog"
    >
      <div class="log-terminal">
        <div v-if="collectLogs.length === 0" class="log-empty">正在获取执行日志...</div>
        <div v-else v-for="(log, index) in collectLogs" :key="index" class="log-line">
          {{ log }}
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="dialogVisible = false">确 定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, computed, ref, watch, onUnmounted } from 'vue'
import { NodeService } from '../api/node.service'
import { MetricService } from '../api/metric.service'
import { useAuthStore } from '../stores/auth'
import CpuChart from '../components/CpuChart.vue'
import MemoryChart from '../components/MemoryChart.vue'
import { ElMessage } from 'element-plus'

const meta = reactive({ uuid: '未选择', name: '-', ip: '-' })
const auth = useAuthStore()
const nodes = reactive<Array<{ name:string; ip:string; status:'healthy'|'warning'|'error'; cpu:string; mem:string; updated:string; error?:string }>>([])
const collecting = ref(false)
const syncing = ref(false)
const isMonitoring = ref(false)
const monitorInterval = ref(5)
const nodeErrors = ref<Record<string, string>>({})
const dialogVisible = ref(false)
const collectLogs = ref<string[]>([])
let pollTimer: any = null

const updateTime = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}年${d.getMonth()+1}月${d.getDate()}日 ${d.getHours()}:${d.getMinutes()}:${d.getSeconds()}`
})

const totalCount = computed(() => nodes.length)
const healthyCount = computed(() => nodes.filter(n => n.status==='healthy').length)
const warningCount = computed(() => nodes.filter(n => n.status==='warning').length)
const errorCount = computed(() => nodes.filter(n => n.status==='error' || n.error).length)

// 监听集群 ID 变化
watch(() => meta.uuid, async (newUuid) => {
  if (newUuid && newUuid !== '未选择') {
    stopPolling() // 切换集群时先停止旧轮询
    await syncMonitorStatus()
    await loadNodes()
  }
})

onMounted(async () => {
  const raw = sessionStorage.getItem('current_cluster')
  if (raw) Object.assign(meta, JSON.parse(raw))
  // 如果 meta.uuid 已经是有效值，watch 可能不会触发（取决于初始值），所以这里补一次
  if (meta.uuid !== '未选择') {
    await syncMonitorStatus()
    await loadNodes()
  }
})

onUnmounted(() => {
  stopPolling()
})

async function syncMonitorStatus() {
  if (meta.uuid === '未选择') return
  syncing.value = true
  try {
    const status = await MetricService.getCollectorStatus(meta.uuid)
    console.log("[DEBUG] Collector Status Response:", status)
    
    // 强制转换为布尔值，防止后端返回 0/1 或 "true"/"false" 导致判断失效
    isMonitoring.value = !!status.is_running 
    monitorInterval.value = status.interval || 5
    nodeErrors.value = status.errors || {}
    
    if (isMonitoring.value) {
      startPolling()
    } else {
      stopPolling()
    }
  } catch (e) {
    console.error("同步监控状态失败", e)
  } finally {
    syncing.value = false
  }
}

function startPolling() {
  if (pollTimer) return
  pollTimer = setInterval(() => {
    loadNodes()
    syncMonitorStatus() // 同时更新错误信息和运行状态
  }, monitorInterval.value * 1000)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

async function collectMetrics() {
  if (meta.uuid === '未选择') {
    ElMessage.warning("请先选择一个集群")
    return
  }
  
  collectLogs.value = []
  dialogVisible.value = true
  collecting.value = true
  
  try {
    collectLogs.value.push(`[${new Date().toLocaleTimeString()}] 正在启动后台采集线程 (周期: ${monitorInterval.value}s)...`)
    await MetricService.startCollector(meta.uuid, monitorInterval.value)
    collectLogs.value.push(`[${new Date().toLocaleTimeString()}] 后台采集器启动成功！`)
    collectLogs.value.push(`[${new Date().toLocaleTimeString()}] 系统将进入自动刷新模式。`)
    
    isMonitoring.value = true
    startPolling()
    ElMessage.success("监控采集器已启动")
  } catch (e: any) {
    const errorMsg = e.friendlyMessage || "启动采集器失败"
    collectLogs.value.push(`[${new Date().toLocaleTimeString()}] 错误: ${errorMsg}`)
    ElMessage.error(errorMsg)
  } finally {
    collecting.value = false
  }
}

async function stopMonitoring() {
  try {
    await MetricService.stopCollector(meta.uuid)
    isMonitoring.value = false
    stopPolling()
    ElMessage.warning("后台监控已停止")
  } catch (e: any) {
    ElMessage.error("停止监控失败")
  }
}

async function loadNodes(){
  if (meta.uuid === '未选择') return
  try{
    const list = await NodeService.listByCluster(meta.uuid)
    nodes.splice(0, nodes.length, ...list.map((x:any)=>({ 
      name:x.name, 
      ip:x.ip, 
      status:x.status, 
      cpu:x.cpu, 
      mem:x.mem, 
      updated:x.updated,
      error: nodeErrors.value[x.name] // 关联后台采集错误
    })))
  }catch(e:any){
    // 自动刷新时的静默失败，手动刷新才报错
    if (!pollTimer) ElMessage.error("获取节点列表失败")
  }
}

async function start(name:string){ 
  try{ 
    await NodeService.start(name)
    ElMessage.success(`${name} 启动成功`)
    await loadNodes() 
  }catch(e:any){
    ElMessage.error("启动失败")
  } 
}

async function stop(name:string){ 
  try{ 
    await NodeService.stop(name)
    ElMessage.warning(`${name} 已停止`)
    await loadNodes() 
  }catch(e:any){
    ElMessage.error("停止失败")
  } 
}

async function remove(name:string){ 
  try{ 
    await NodeService.remove(name)
    ElMessage.success(`${name} 已删除`)
    await loadNodes() 
  }catch(e:any){
    ElMessage.error("删除失败")
  } 
}
</script>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  margin-bottom: 8px;
}

.header-main {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--app-text-primary);
  margin: 0;
}

.stats-row {
  margin-bottom: 4px;
}

.stat-card {
  border-radius: 8px;
}

.charts-row {
  margin-top: 4px;
}

.nodes-card {
  margin-top: 4px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.font-bold {
  font-weight: 600;
}

/* 终端样式弹窗 */
.log-terminal {
  background-color: #1e1e1e;
  color: #d4d4d4;
  padding: 16px;
  border-radius: 4px;
  font-family: 'Courier New', Courier, monospace;
  min-height: 200px;
  max-height: 400px;
  overflow-y: auto;
}

.log-empty {
  color: #888;
  font-style: italic;
  text-align: center;
  margin-top: 80px;
}

.log-line {
  margin-bottom: 8px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
