<template>
  <section class="layout__section" aria-labelledby="operation-logs-title">
    <header class="layout__page-header">
      <div>
        <h2 id="operation-logs-title" class="layout__page-title">系统操作日志</h2>
        <p class="layout__page-subtitle">记录用户操作与系统事件</p>
      </div>
      <div class="layout__page-actions">
        <button class="btn" @click="refresh" :disabled="loading">刷新</button>
        <button class="btn btn--primary u-ml-1" disabled title="功能待实现">导出操作日志</button>
      </div>
    </header>

    <article class="layout__card">
      <div class="layout__card-header">
        <h3 class="layout__card-title">近期操作事件</h3>
      </div>
      <div class="layout__card-body u-p-0">
        <div v-if="loading" class="u-p-4 u-text-center">加载中...</div>
        <div v-else-if="err" class="u-p-4 u-text-center u-text-error">{{ err }}</div>
        <div v-else class="u-overflow-x-auto">
          <table class="dashboard__table">
            <thead class="dashboard__table-head">
              <tr>
                <th class="dashboard__table-th" scope="col">时间</th>
                <th class="dashboard__table-th" scope="col">用户</th>
                <th class="dashboard__table-th" scope="col">详情</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in logs" :key="log.id" class="dashboard__table-row">
                <td class="dashboard__table-td"><time :datetime="log.timestamp">{{ formatTime(log.timestamp) }}</time></td>
                <td class="dashboard__table-td">{{ log.user }}</td>
                <td class="dashboard__table-td">{{ log.detail }}</td>
              </tr>
              <tr v-if="logs.length === 0" class="dashboard__table-row">
                <td colspan="3" class="dashboard__table-td u-text-center">暂无操作记录</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import api from '../lib/api'
import { useAuthStore } from '../stores/auth'

interface OperationLogItem {
  id: string
  timestamp: string
  user: string
  detail: string
}

const auth = useAuthStore()
const logs = reactive<OperationLogItem[]>([])
const loading = ref(false)
const err = ref('')

function formatTime(ts: string) {
  if (!ts) return '-'
  return ts.replace('T', ' ').slice(0, 19)
}

async function refresh() {
  await loadLogs()
}

async function loadLogs() {
  loading.value = true
  err.value = ''
  try {
    const r = await api.get('/v1/sys-exec-logs', {
      headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined
    })
    
    // 适配新的数据结构
    const items = Array.isArray(r.data?.items) ? r.data.items : (Array.isArray(r.data?.operation_logs) ? r.data.operation_logs : [])
    
    const normalized: OperationLogItem[] = items.map((d: any) => ({
      id: d.operation_id || d.id,
      timestamp: d.operation_time || d.timestamp || d.created_at || d.time,
      user: d.user || d.username || d.operator || `User ${d.user_id}`,
      detail: d.detail || d.description || d.content
    }))
    
    logs.splice(0, logs.length, ...normalized)
  } catch (e: any) {
    const status = e.response?.status
    const detail = e.response?.data?.detail
    
    if (status === 401) {
      err.value = '会话已过期或未登录，请重新登录后再试。'
    } else if (status === 403) {
      err.value = '权限不足：只有管理员角色可以查看操作日志。'
    } else if (status === 404) {
      err.value = '未找到操作日志接口 (404)，请联系后端开发人员确认 API 端点。'
    } else if (status === 500) {
      err.value = '后端服务器内部错误 (500)，请稍后重试或检查后端日志。'
    } else if (status === 502 || status === 504) {
      err.value = '后端网关错误或超时 (502/504)，请检查后端服务是否正常运行。'
    } else {
      err.value = `加载操作日志失败：${detail || e.message || '请检查网络连接或后端服务状态'}`
    }
    
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
.u-p-4 { padding: 1.5rem; }
.u-text-center { text-align: center; }
.u-text-error { color: #dc2626; }
.u-ml-1 { margin-left: 0.25rem; }
</style>
