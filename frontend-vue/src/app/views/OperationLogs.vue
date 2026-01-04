<template>
  <div class="operation-logs-container">
    <div class="page-header">
      <div class="header-content">
        <h2 class="page-title">系统操作日志</h2>
        <p class="page-subtitle">记录用户操作与系统事件</p>
      </div>
      <div class="header-actions">
        <el-button @click="refresh" :loading="loading">刷新</el-button>
        <el-button type="primary" disabled title="功能待实现">导出操作日志</el-button>
      </div>
    </div>

    <el-card class="table-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>近期操作事件</span>
        </div>
      </template>
      <el-table
        v-loading="loading"
        :data="logs"
        stripe
        style="width: 100%"
        header-cell-class-name="table-header"
      >
        <el-table-column label="时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.timestamp) }}
          </template>
        </el-table-column>
        <el-table-column prop="user" label="用户" width="150" />
        <el-table-column prop="detail" label="详情" min-width="300" show-overflow-tooltip />
        <template #empty>
          <el-empty description="暂无操作记录" />
        </template>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { LogService } from '../api/log.service'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

interface OperationLogItem {
  id: string
  timestamp: string
  user: string
  detail: string
}

const auth = useAuthStore()
const logs = reactive<OperationLogItem[]>([])
const loading = ref(false)

function formatTime(ts: string) {
  if (!ts) return '-'
  return ts.replace('T', ' ').slice(0, 19)
}

async function refresh() {
  await loadLogs()
}

async function loadLogs() {
  loading.value = true
  try {
    const items = await LogService.listOperationLogs()
    
    const normalized: OperationLogItem[] = items.map((d: any) => ({
      id: d.operation_id || d.id,
      timestamp: d.operation_time || d.timestamp || d.created_at || d.time,
      user: d.user || d.username || d.operator || `User ${d.user_id}`,
      detail: d.detail || d.description || d.content
    }))
    
    logs.splice(0, logs.length, ...normalized)
  } catch (e: any) {
    ElMessage.error(e.friendlyMessage || '加载操作日志失败')
    logs.splice(0, logs.length)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.operation-logs-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.table-card {
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.card-header {
  font-weight: 600;
}

:deep(.table-header) {
  background-color: #f8fafc !important;
  color: #475569;
  font-weight: 600;
}
</style>
