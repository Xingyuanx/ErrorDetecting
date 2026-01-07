<template>
  <div class="logs-container">
    <div class="page-header">
      <h2 class="page-title">集群日志</h2>
    </div>

    <el-card class="filter-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>搜索条件</span>
          <el-button type="primary" link @click="clear">清除筛选</el-button>
        </div>
      </template>
      
      <el-form :model="q" label-position="top" size="default">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item label="来源集群">
              <el-select v-model="q.cluster" placeholder="全部集群" clearable class="w-full">
                <el-option v-for="c in clustersOpts" :key="c" :label="c" :value="c" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item label="来源节点">
              <el-select v-model="q.node" placeholder="全部节点" clearable class="w-full">
                <el-option v-for="n in nodesOpts" :key="n" :label="n" :value="n" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item label="时间范围">
              <el-select v-model="q.timeRange" placeholder="全部时间" clearable class="w-full">
                <el-option label="最近1小时" value="1h" />
                <el-option label="最近6小时" value="6h" />
                <el-option label="最近24小时" value="24h" />
                <el-option label="最近7天" value="7d" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <div class="filter-summary">
        <el-tag type="info" variant="plain" size="small">当前筛选：{{ summary }}</el-tag>
      </div>
    </el-card>

    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="pageData"
        stripe
        style="width: 100%"
        header-cell-class-name="table-header"
      >
        <el-table-column label="时间" width="180">
          <template #default="{ row }">
            {{ row.time }}
          </template>
        </el-table-column>
        <el-table-column prop="cluster" label="集群" width="150" show-overflow-tooltip />
        <el-table-column prop="node" label="节点" width="150" show-overflow-tooltip />
        <el-table-column prop="info" label="详细内容" min-width="300" show-overflow-tooltip />
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="size"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch, onMounted } from 'vue'
import { LogService } from '../api/log.service'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const data = ref<{ id:number|string; time:string; cluster:string; node:string; info:string }[]>([])
const page = ref(1)
const size = ref(20)
const total = ref(0)
const loading = ref(false)
const err = ref('')
const q = reactive({ cluster:'', node:'', timeRange:'' })
const clustersOpts = ref<string[]>([])
const nodesOpts = ref<string[]>([])

function rangeFromNow(r:string){
  const now = Date.now()
  const span = r==='1h'?60*60*1000:r==='6h'?6*60*60*1000:r==='24h'?24*60*60*1000:r==='7d'?7*24*60*60*1000:0
  return span? new Date(now-span).toISOString() : ''
}

async function load(){
  loading.value = true
  err.value = ''
  try{
    const params: any = { page: page.value, size: size.value }
    if (q.cluster) params.cluster = q.cluster
    if (q.node) params.node = q.node
    if (q.timeRange) params.time_from = rangeFromNow(q.timeRange)
    
    const { items, total: t } = await LogService.list(params)
    const normalized = items.map((d:any)=>({
      id: d.id,
      time: d.time || '',
      cluster: d.cluster || '',
      node: d.node || '',
      info: d.info || ''
    }))
    data.value = normalized
    total.value = t
    
    if (!clustersOpts.value.length) clustersOpts.value = Array.from(new Set(items.map((d:any)=>d.cluster).filter(Boolean)))
    if (!nodesOpts.value.length) nodesOpts.value = Array.from(new Set(items.map((d:any)=>d.node).filter(Boolean)))
  }catch(e:any){ 
    err.value = e.friendlyMessage || e?.response?.data?.detail || '加载失败' 
  } finally{ 
    loading.value = false 
  }
}

function clear() { 
  q.cluster=''; q.node=''; q.timeRange=''; 
  page.value=1 
}

const handleSizeChange = (val: number) => {
  size.value = val
  page.value = 1
  load()
}

const handleCurrentChange = (val: number) => {
  page.value = val
  load()
}

const pageData = computed(() => data.value)

// 监听筛选条件变化
watch(() => ({...q}), () => {
  page.value = 1
  load()
}, { deep: true })

onMounted(()=>{ load() })

const summary = computed(() => {
  const parts = [] as string[]
  if (q.cluster) parts.push(`集群=${q.cluster}`)
  if (q.node) parts.push(`节点=${q.node}`)
  if (q.timeRange) parts.push(`时间=${q.timeRange}`)
  return parts.length? parts.join('，') : '无'
})
</script>

<style scoped>
.logs-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  margin-bottom: 8px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.filter-card, .table-card {
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.filter-summary {
  margin-top: 12px;
}

.w-full {
  width: 100%;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.table-header) {
  background-color: #f8fafc !important;
  color: #475569;
  font-weight: 600;
}
</style>
