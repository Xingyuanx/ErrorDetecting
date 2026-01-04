<template>
  <div class="dashboard-container">
    <div class="page-header">
      <div class="header-main">
        <h2 class="page-title">仪表板 · 集群概览</h2>
        <el-tag type="info" effect="plain" class="update-time">
          更新时间：{{ updateTime }}
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
          <el-statistic title="健康节点" :value="healthyCount" value-style="color: #16a34a" />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="警告节点" :value="warningCount" value-style="color: #f59e0b" />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="异常节点" :value="errorCount" value-style="color: #dc2626" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="charts-row">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" header="CPU 使用率趋势">
          <CpuChart :cluster="meta.uuid" />
        </el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" header="内存使用率趋势">
          <MemoryChart :cluster="meta.uuid" />
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" class="nodes-card">
      <template #header>
        <div class="card-header">
          <span>节点状态详情</span>
          <el-button type="primary" link @click="loadNodes">刷新数据</el-button>
        </div>
      </template>
      <el-table :data="nodes" style="width: 100%" stripe>
        <el-table-column prop="name" label="节点名称" min-width="120">
          <template #default="{ row }">
            <span class="font-bold">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="ip" label="IP 地址" width="140" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">
              {{ statusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="cpu" label="CPU 使用率" width="120" />
        <el-table-column prop="mem" label="内存使用" width="120" />
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
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, computed } from 'vue'
import { NodeService } from '../api/node.service'
import { useAuthStore } from '../stores/auth'
import CpuChart from '../components/CpuChart.vue'
import MemoryChart from '../components/MemoryChart.vue'
import { ElMessage } from 'element-plus'

const meta = reactive({ uuid: '未选择', name: '-', ip: '-' })
const auth = useAuthStore()
const nodes = reactive<Array<{ name:string; ip:string; status:'healthy'|'warning'|'error'; cpu:string; mem:string; updated:string }>>([])

const updateTime = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}年${d.getMonth()+1}月${d.getDate()}日`
})

const totalCount = computed(() => nodes.length)
const healthyCount = computed(() => nodes.filter(n => n.status==='healthy').length)
const warningCount = computed(() => nodes.filter(n => n.status==='warning').length)
const errorCount = computed(() => nodes.filter(n => n.status==='error').length)

onMounted(() => {
  const raw = sessionStorage.getItem('current_cluster')
  if (raw) Object.assign(meta, JSON.parse(raw))
  loadNodes()
})

async function loadNodes(){
  try{
    const list = await NodeService.listByCluster(meta.uuid)
    nodes.splice(0, nodes.length, ...list.map((x:any)=>({ 
      name:x.name, 
      ip:x.ip, 
      status:x.status, 
      cpu:x.cpu, 
      mem:x.mem, 
      updated:x.updated 
    })))
  }catch(e:any){
    ElMessage.error("获取节点列表失败")
  }
}

function statusText(s:'healthy'|'warning'|'error'){ 
  return s==='healthy'?'运行中':s==='warning'?'警告':'异常' 
}

function statusTagType(s:'healthy'|'warning'|'error'){ 
  return s==='healthy'?'success':s==='warning'?'warning':'danger' 
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
  color: #1e293b;
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

.font-bold {
  font-weight: 600;
}
</style>
