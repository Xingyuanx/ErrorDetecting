<template>
  <div class="cluster-list-container">
    <div class="page-header">
      <div class="header-content">
        <h2 class="page-title">集群列表</h2>
        <p class="page-subtitle">管理并监控所有已注册的大数据集群</p>
      </div>
      <el-button type="primary" @click="showRegister = true" v-if="!showRegister">
        <el-icon class="btn-icon"><Plus /></el-icon>注册新集群
      </el-button>
    </div>

    <!-- 注册表单卡片 -->
    <el-collapse-transition>
      <el-card v-if="showRegister" class="register-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span class="card-title">注册新集群</span>
            <el-button link @click="cancelRegister">取消</el-button>
          </div>
        </template>

        <el-form :model="registerForm" label-position="top" size="default">
          <h4 class="section-subtitle">1. 集群基本信息</h4>
          <el-row :gutter="20">
            <el-col :span="6">
              <el-form-item label="集群名称" required>
                <el-input v-model="registerForm.name" placeholder="集群名称" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="集群类型">
                <el-select v-model="registerForm.type" class="full-width">
                  <el-option label="Hadoop" value="hadoop" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="节点总数">
                <el-input-number v-model="registerForm.node_count" :min="1" class="full-width" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="健康状态">
                <el-select v-model="registerForm.health_status" class="full-width">
                  <el-option label="健康" value="healthy" />
                  <el-option label="警告" value="warning" />
                  <el-option label="异常" value="error" />
                  <el-option label="未知" value="unknown" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="6">
              <el-form-item label="NameNode IP">
                <el-input v-model="registerForm.namenode_ip" placeholder="NameNode IP" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="NameNode 密码">
                <el-input v-model="registerForm.namenode_psw" type="password" show-password placeholder="NameNode 密码" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="RM IP">
                <el-input v-model="registerForm.rm_ip" placeholder="ResourceManager IP" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="RM 密码">
                <el-input v-model="registerForm.rm_psw" type="password" show-password placeholder="ResourceManager 密码" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="集群描述">
            <el-input v-model="registerForm.description" type="textarea" :rows="2" placeholder="集群描述 (可选)" />
          </el-form-item>

          <h4 class="section-subtitle section-mt">2. 节点详细配置</h4>
          <div v-for="(node, idx) in nodes" :key="idx" class="node-config-row">
            <div class="node-index">节点 {{ idx + 1 }}</div>
            <el-row :gutter="10">
              <el-col :span="6">
                <el-form-item label="主机名" required>
                  <el-input v-model="node.hostname" placeholder="hostname" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="IP 地址" required>
                  <el-input v-model="node.ip_address" placeholder="ip_address" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="SSH 用户" required>
                  <el-input v-model="node.ssh_user" placeholder="ssh_user" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="SSH 密码" required>
                  <el-input v-model="node.ssh_password" type="password" show-password placeholder="ssh_password" />
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <div class="form-actions">
            <el-button type="primary" :loading="registering" @click="onRegister">提交注册</el-button>
            <el-button @click="cancelRegister">取消</el-button>
          </div>
          <el-alert v-if="err" :title="err" type="error" show-icon class="form-alert" @close="err = ''" />
        </el-form>
      </el-card>
    </el-collapse-transition>

    <!-- 集群列表表格 -->
    <el-card shadow="never" class="table-card">
      <el-table
        :data="clusters"
        style="width: 100%"
        stripe
        v-loading="loading"
        @row-click="toDashboard"
        class="cluster-table"
        header-cell-class-name="table-header"
      >
        <el-table-column prop="name" label="集群名" :min-width="isMobile ? 100 : 150" />
        <el-table-column v-if="!isMobile" prop="node_count" label="节点数" width="100" align="center" />
        <el-table-column prop="health_status" label="健康状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getHealthTag(row.health_status)" effect="light">
              {{ row.healthText }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" :width="isMobile ? 120 : 420" fixed="right">
          <template #default="{ row }">
            <div v-if="!isMobile" class="table-actions" @click.stop>
              <el-button size="small" @click="toDashboard(row)">详情</el-button>
              <el-button
                size="small"
                type="success"
                plain
                :disabled="row.health_status === 'healthy'"
                :loading="rowLoading[row.uuid]"
                @click="startCluster(row)"
              >启动</el-button>
              <el-button
                size="small"
                type="warning"
                plain
                :disabled="row.health_status !== 'healthy'"
                :loading="rowLoading[row.uuid]"
                @click.stop="stopCluster(row)"
              >停止</el-button>
              <div class="switch-action" @click.stop>
                <span class="switch-label">采集日志</span>
                <el-switch
                  v-model="clusterStore.collectionStates[row.uuid]"
                  :loading="rowLoading[row.uuid]"
                  @change="(val: boolean) => handleCollectionChange(val, row)"
                  active-color="#13ce66"
                />
              </div>
              <el-popconfirm title="确定要注销此集群吗？" @confirm="unregister(row.uuid)">
                <template #reference>
                  <el-button size="small" type="danger" plain>注销</el-button>
                </template>
              </el-popconfirm>
            </div>
            <div v-else class="mobile-actions" @click.stop>
              <el-dropdown trigger="click" @command="(cmd: string) => handleAction(cmd, row)">
                <el-button size="small" type="primary" plain :loading="rowLoading[row.uuid]">
                  操作<el-icon class="el-icon--right" v-if="!rowLoading[row.uuid]"><More /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item header class="dropdown-header">{{ row.name }}</el-dropdown-item>
                    <el-dropdown-item command="details">详情</el-dropdown-item>
                    <el-dropdown-item 
                      command="start" 
                      :disabled="row.health_status === 'healthy'"
                    >启动</el-dropdown-item>
                    <el-dropdown-item 
                      command="stop" 
                      :disabled="row.health_status !== 'healthy'"
                    >停止</el-dropdown-item>
                    <el-dropdown-item command="collect">采集日志</el-dropdown-item>
                    <el-dropdown-item command="unregister" divided class="text-danger">注销</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 操作日志弹窗 -->
    <el-dialog
      v-model="showLogs"
      :title="logTitle"
      width="60%"
      destroy-on-close
      class="log-dialog"
    >
      <div class="log-terminal">
        <div v-for="(line, idx) in executionLogs" :key="idx" class="log-line">
          <span class="log-timestamp">[{{ new Date().toLocaleTimeString() }}]</span>
          <span class="log-content">{{ line }}</span>
        </div>
        <div v-if="executionLogs.length === 0" class="log-empty">正在获取执行日志...</div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="showLogs = false">确 定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ClusterService } from '../api/cluster.service'
import { LogService } from '../api/log.service'
import { useClusterStore } from '../stores/cluster'
import { Plus, More } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const clusterStore = useClusterStore()
const clusters = ref<any[]>([])
const showRegister = ref(false)
const loading = ref(false)
const registering = ref(false)
const err = ref('')
const rowLoading = ref<Record<string, boolean>>({})

// 日志相关状态
const showLogs = ref(false)
const logTitle = ref('')
const executionLogs = ref<string[]>([])

const isMobile = ref(window.innerWidth < 768)
const updateWidth = () => {
  isMobile.value = window.innerWidth < 768
}

const registerForm = reactive({
  name: '',
  type: 'hadoop',
  node_count: 1,
  health_status: 'unknown',
  namenode_ip: '',
  namenode_psw: '',
  rm_ip: '',
  rm_psw: '',
  description: ''
})

const nodes = ref<any[]>([
  { hostname: '', ip_address: '', ssh_user: 'hadoop', ssh_password: '' }
])

watch(() => registerForm.node_count, (newVal) => {
  const target = Number(newVal)
  if (!target || target < 1) return
  const current = nodes.value.length
  if (target > current) {
    for (let i = current; i < target; i++) {
      nodes.value.push({ hostname: '', ip_address: '', ssh_user: 'hadoop', ssh_password: '' })
    }
  } else if (target < current) {
    nodes.value = nodes.value.slice(0, target)
  }
})

function cancelRegister() {
  showRegister.value = false
  err.value = ''
  Object.assign(registerForm, {
    name: '',
    type: 'hadoop',
    node_count: 1,
    health_status: 'unknown',
    namenode_ip: '',
    namenode_psw: '',
    rm_ip: '',
    rm_psw: '',
    description: ''
  })
  nodes.value = [{ hostname: '', ip_address: '', ssh_user: 'hadoop', ssh_password: '' }]
}

function healthTextOf(h: string) {
  const map: any = { healthy: '健康', warning: '警告', error: '异常', unknown: '未知' }
  return map[h] || '未知'
}

function getHealthTag(h: string) {
  const map: any = { healthy: 'success', warning: 'warning', error: 'danger', unknown: 'info' }
  return map[h] || 'info'
}

function formatError(e: any, defaultMsg: string = '操作失败'): string {
  if (e?.response) {
    const s = e.response.status
    const d = e.response.data
    let detail = ''
    if (d?.detail) {
      if (typeof d.detail === 'string') detail = d.detail
      else if (Array.isArray(d.detail?.errors)) {
        detail = d.detail.errors.map((x: any) => {
          let msg = x?.message || '未知错误'
          if (x?.field) msg = `[${x.field}] ${msg}`
          return msg
        }).join(', ')
      }
    }
    return detail || `请求异常 (${s})`
  }
  return e?.message || defaultMsg
}

async function load() {
  loading.value = true
  try {
    const list = await ClusterService.list()
    clusters.value = list.map((x: any) => ({
      uuid: x.uuid,
      name: x.name || x.host || '',
      node_count: Number(x.node_count || x.count) || 0,
      health_status: x.health_status || x.health || 'unknown',
      healthText: healthTextOf(x.health_status || x.health)
    }))
    
    // 初始化采集状态（可选：根据后端状态接口初始化）
    await syncCollectionStatus()
  } catch (e: any) {
    ElMessage.error(e.friendlyMessage || formatError(e, '加载列表失败'))
  } finally {
    loading.value = false
  }
}

/** 同步采集状态 */
async function syncCollectionStatus() {
  try {
    const status = await LogService.getCollectorStatus()
    // 假设 status 包含正在采集的集群 UUID 列表或其他标识
    // 这里根据后端实际返回结构进行映射，目前先根据 clusters 列表初始化
    const newStates: Record<string, boolean> = {}
    clusters.value.forEach(c => {
      if (clusterStore.collectionStates[c.uuid] === undefined) {
        newStates[c.uuid] = false
      }
    })
    clusterStore.syncStates(newStates)
  } catch (e) {
    console.error('获取采集状态失败', e)
  }
}

async function onRegister() {
  if (!registerForm.name) {
    ElMessage.warning('请填写集群名称')
    return
  }
  
  for (let i = 0; i < nodes.value.length; i++) {
    const n = nodes.value[i]
    if (!n.hostname || !n.ip_address || !n.ssh_user || !n.ssh_password) {
      ElMessage.warning(`请完善第 ${i + 1} 个节点的信息`)
      return
    }
  }

  registering.value = true
  err.value = ''
  try {
    const payload = {
      ...registerForm,
      nodes: nodes.value
    }
    await ClusterService.register(payload)
    ElMessage.success('集群注册成功')
    cancelRegister()
    await load()
  } catch (e: any) {
    err.value = e.friendlyMessage || formatError(e, '提交失败')
  } finally {
    registering.value = false
  }
}

async function unregister(id: string) {
  try {
    await ClusterService.unregister(id)
    ElMessage.success('集群已注销')
    await load()
  } catch (e: any) {
    ElMessage.error(e.friendlyMessage || formatError(e, '注销失败'))
  }
}

async function startCluster(row: any) {
  const id = typeof row === 'string' ? row : row.uuid
  const name = typeof row === 'string' ? id : row.name
  
  rowLoading.value[id] = true
  logTitle.value = `正在启动集群: ${name}`
  executionLogs.value = []
  showLogs.value = true
  
  try {
    const res = await ClusterService.start(id)
    executionLogs.value = res.logs || ['启动指令已成功发送，正在执行...']
    ElMessage.success('启动成功')
    await load()
  } catch (e: any) {
    executionLogs.value = e.response?.data?.logs || [e.message || '启动失败']
    ElMessage.error(e.friendlyMessage || formatError(e, '启动失败'))
  } finally {
    rowLoading.value[id] = false
  }
}

async function stopCluster(row: any) {
  const id = typeof row === 'string' ? row : row.uuid
  const name = typeof row === 'string' ? id : row.name
  
  rowLoading.value[id] = true
  logTitle.value = `正在停止集群: ${name}`
  executionLogs.value = []
  showLogs.value = true
  
  try {
    const res = await ClusterService.stop(id)
    executionLogs.value = res.logs || ['停止指令已成功发送，正在执行...']
    ElMessage.success('停止成功')
    await load()
  } catch (e: any) {
    executionLogs.value = e.response?.data?.logs || [e.message || '停止失败']
    ElMessage.error(e.friendlyMessage || formatError(e, '关闭失败'))
  } finally {
    rowLoading.value[id] = false
  }
}

async function handleCollectionChange(val: boolean, row: any) {
  if (val) {
    await collectLogs(row)
  } else {
    await stopLogs(row)
  }
}

async function collectLogs(row: any) {
  const id = row.uuid
  const name = row.name
  
  rowLoading.value[id] = true
  logTitle.value = `正在启动采集: ${name}`
  executionLogs.value = []
  showLogs.value = true
  
  try {
    const res = await LogService.startHadoopCollection(id)
    executionLogs.value = res.logs || ['日志采集任务已启动...']
    ElMessage.success('日志采集任务已启动')
    clusterStore.setCollectionState(id, true)
  } catch (e: any) {
    executionLogs.value = e.response?.data?.logs || [e.message || '启动采集失败']
    ElMessage.error(formatError(e, '启动日志采集失败'))
    clusterStore.setCollectionState(id, false) // 失败则切回关闭状态
  } finally {
    rowLoading.value[id] = false
  }
}

async function stopLogs(row: any) {
  const id = row.uuid
  rowLoading.value[id] = true
  logTitle.value = `正在停止采集: ${row.name}`
  executionLogs.value = []
  showLogs.value = true

  try {
    const res = await LogService.stopAllCollections()
    executionLogs.value = res.logs || ['已发送停止全部采集指令...']
    ElMessage.warning('所有采集任务已停止')
    // 停止全部采集，更新所有集群状态
    const newStates: Record<string, boolean> = {}
    clusters.value.forEach(c => { newStates[c.uuid] = false })
    clusterStore.syncStates(newStates)
  } catch (e: any) {
    executionLogs.value = e.response?.data?.logs || [e.message || '停止失败']
    ElMessage.error(formatError(e, '停止采集失败'))
    clusterStore.setCollectionState(id, true) // 失败则切回开启状态
  } finally {
    rowLoading.value[id] = false
  }
}

function toDashboard(c: any) {
  sessionStorage.setItem('current_cluster', JSON.stringify(c))
  router.push({ name: 'dashboard' })
}

function handleAction(command: string, row: any) {
  switch (command) {
    case 'details':
      toDashboard(row);
      break;
    case 'start':
      startCluster(row);
      break;
    case 'stop':
      stopCluster(row);
      break;
    case 'collect':
      collectLogs(row);
      break;
    case 'unregister':
      ElMessageBox.confirm('确定要注销此集群吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        unregister(row.uuid);
      }).catch(() => {});
      break;
  }
}

onMounted(() => {
  load()
  window.addEventListener('resize', updateWidth)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateWidth)
})
</script>

<style scoped>
.cluster-list-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--app-text-primary);
  margin: 0;
}

.page-subtitle {
  color: var(--app-text-secondary);
  font-size: 14px;
  margin: 4px 0 0 0;
}

.btn-icon {
  margin-right: 4px;
}

.register-card {
  margin-bottom: 8px;
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-weight: 600;
}

.section-subtitle {
  margin: 0 0 16px 0;
  font-size: 15px;
  color: var(--app-text-primary);
  border-left: 4px solid var(--el-color-primary);
  padding-left: 10px;
}

.section-mt {
  margin-top: 24px;
}

.node-config-row {
  margin-bottom: 16px;
  padding: 16px;
  border: 1px solid var(--app-border-color);
  border-radius: 6px;
  background-color: var(--app-content-bg);
  transition: background-color 0.3s;
}

.node-config-row:hover {
  background-color: var(--app-bg);
}

.node-index {
  font-weight: 600;
  margin-bottom: 12px;
  font-size: 14px;
  color: var(--app-text-secondary);
}

.form-actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
}

.form-alert {
  margin-top: 16px;
}

.table-card {
  border-radius: 8px;
  border: 1px solid var(--app-border-color);
}

.cluster-table {
  cursor: pointer;
}

.table-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-start;
  align-items: center;
}

.switch-action {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 8px;
  background-color: var(--app-bg);
  border-radius: 4px;
  height: 32px;
  border: 1px solid var(--app-border-color);
}

.switch-label {
  font-size: 12px;
  color: var(--app-text-secondary);
  white-space: nowrap;
}

.full-width {
  width: 100%;
}

:deep(.table-header) {
  background-color: var(--app-content-bg) !important;
  color: var(--app-text-secondary);
  font-weight: 600;
}

.dropdown-header {
  font-weight: bold;
  color: var(--app-text-primary);
  padding: 8px 16px;
  border-bottom: 1px solid var(--app-border-color);
  pointer-events: none;
}

.text-danger {
  color: #ef4444;
}

.mobile-actions {
  display: flex;
  justify-content: center;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .header-content {
    width: 100%;
  }

  :deep(.el-table .cell) {
    padding: 0 4px;
  }
}
</style>
