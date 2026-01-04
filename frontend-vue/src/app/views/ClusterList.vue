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
        <el-table-column label="操作" :width="isMobile ? 120 : 350" fixed="right">
          <template #default="{ row }">
            <div v-if="!isMobile" class="table-actions" @click.stop>
              <el-button size="small" @click="toDashboard(row)">详情</el-button>
              <el-button
                size="small"
                type="success"
                plain
                :disabled="row.health_status === 'healthy'"
                :loading="rowLoading[row.uuid]"
                @click="startCluster(row.uuid)"
              >启动</el-button>
              <el-button
                size="small"
                type="warning"
                plain
                :disabled="row.health_status !== 'healthy'"
                :loading="rowLoading[row.uuid]"
                @click="stopCluster(row.uuid)"
              >停止</el-button>
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
                    <el-dropdown-item command="unregister" divided class="text-danger">注销</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ClusterService } from '../api/cluster.service'
import { Plus, More } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const clusters = ref<any[]>([])
const showRegister = ref(false)
const loading = ref(false)
const registering = ref(false)
const err = ref('')
const rowLoading = ref<Record<string, boolean>>({})

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
  } catch (e: any) {
    ElMessage.error(e.friendlyMessage || formatError(e, '加载列表失败'))
  } finally {
    loading.value = false
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

async function startCluster(id: string) {
  rowLoading.value[id] = true
  const msg = ElMessage({
    message: '正在发送启动命令...',
    type: 'info',
    duration: 0
  })
  try {
    await ClusterService.start(id)
    msg.close()
    ElMessage.success('启动命令已发送')
    await load()
  } catch (e: any) {
    msg.close()
    ElMessage.error(e.friendlyMessage || formatError(e, '启动失败'))
  } finally {
    rowLoading.value[id] = false
  }
}

async function stopCluster(id: string) {
  rowLoading.value[id] = true
  const msg = ElMessage({
    message: '正在发送停止命令...',
    type: 'info',
    duration: 0
  })
  try {
    await ClusterService.stop(id)
    msg.close()
    ElMessage.success('停止命令已发送')
    await load()
  } catch (e: any) {
    msg.close()
    ElMessage.error(e.friendlyMessage || formatError(e, '关闭失败'))
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
      startCluster(row.uuid);
      break;
    case 'stop':
      stopCluster(row.uuid);
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
  color: #1f2937;
  margin: 0;
}

.page-subtitle {
  color: #6b7280;
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
  color: #1e293b;
  border-left: 4px solid #0ea5e9;
  padding-left: 10px;
}

.section-mt {
  margin-top: 24px;
}

.node-config-row {
  margin-bottom: 16px;
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background-color: #f8fafc;
  transition: background-color 0.3s;
}

.node-config-row:hover {
  background-color: #f1f5f9;
}

.node-index {
  font-weight: 600;
  margin-bottom: 12px;
  font-size: 14px;
  color: #475569;
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
  border: 1px solid #ebeef5;
}

.cluster-table {
  cursor: pointer;
}

.table-actions {
  display: flex;
  gap: 8px;
}

.full-width {
  width: 100%;
}

:deep(.table-header) {
  background-color: #f8fafc !important;
  color: #475569;
  font-weight: 600;
}

.dropdown-header {
  font-weight: bold;
  color: #333;
  padding: 8px 16px;
  border-bottom: 1px solid #f0f0f0;
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
