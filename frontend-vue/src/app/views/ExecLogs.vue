<template>
  <div class="exec-logs-container">
    <div class="page-header">
      <div class="header-content">
        <h2 class="page-title">集群操作日志</h2>
        <p class="page-subtitle">查看与管理修复执行记录，支持完整后端同步</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="handleCreate">新增记录</el-button>
      </div>
    </div>

    <el-card class="table-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>执行记录</span>
        </div>
      </template>
      <ExecLogsTable
        :records="records"
        :selected-id="selected"
        @select="select"
        @edit="handleEdit"
        @delete="del"
      />
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="openCreate ? '新增记录' : '编辑记录'"
      :width="isMobile ? '95%' : '600px'"
      @closed="cancelForm"
    >
      <el-form :model="form" label-width="100px" label-position="right">
        <el-form-item label="集群名称" required>
          <el-input v-model="form.clusterName" placeholder="请输入集群名称" />
        </el-form-item>
        <el-form-item label="用户">
          <el-input v-model="form.username" placeholder="请输入用户" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" placeholder="请选择状态" class="w-full">
            <el-option label="Running" value="running" />
            <el-option label="Success" value="success" />
            <el-option label="Failed" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间" required>
          <el-date-picker
            v-model="form.start"
            type="datetime"
            placeholder="请选择开始时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            class="w-full"
          />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker
            v-model="form.end"
            type="datetime"
            placeholder="请选择结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            class="w-full"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="save">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, onUnmounted } from 'vue'
import { LogService } from '../api/log.service'
import { useAuthStore } from '../stores/auth'
import ExecLogsTable from '../components/ExecLogsTable.vue'
import { ElMessage } from 'element-plus'

type RecordItem = { id:number; clusterName:string; username:string; description:string; faultId:string; cmdType:string; status:'running'|'success'|'failed'; start:string; end:string|''; code:number|null }

const isMobile = ref(window.innerWidth < 768)
const updateWidth = () => { isMobile.value = window.innerWidth < 768 }

const auth = useAuthStore()
const records = reactive<RecordItem[]>([])
const selected = ref<number|null>(null)
const openCreate = ref(false)
const openEditForm = ref(false)
const dialogVisible = ref(false)
const saving = ref(false)
const loading = ref(false)
const form = reactive<RecordItem>({ id:0, clusterName:'', username:'', description:'', faultId:'', cmdType:'shell', status:'running', start:'', end:'', code:null })

function select(r: RecordItem){ selected.value = r.id }

function handleCreate() {
  openCreate.value = true
  openEditForm.value = false
  dialogVisible.value = true
}

function handleEdit(r: RecordItem) {
  selected.value = r.id
  openCreate.value = false
  openEditForm.value = true
  Object.assign(form, r)
  dialogVisible.value = true
}

async function del(id:number){
  try{
    await LogService.removeExecLog(id)
    const i = records.findIndex(x=>x.id===id)
    if (i>=0) { 
      records.splice(i,1)
      if (selected.value===id) selected.value=null 
    }
    ElMessage.success('删除成功')
  }catch(e:any){ 
    ElMessage.error('删除失败：' + (e.friendlyMessage || e.message || '网络错误'))
  }
}

function cancelForm(){ 
  openCreate.value=false; 
  openEditForm.value=false; 
  Object.assign(form, { id:0, clusterName:'', username:'', description:'', faultId:'', cmdType:'shell', status:'running', start:'', end:'', code:null }) 
}

async function save(){
  if (!form.clusterName || !form.start) { 
    ElMessage.warning('请完整填写必填信息')
    return 
  }
  
  const payload = { 
    from_user_id: auth.user?.id || 0,
    cluster_name: form.clusterName,
    description: form.description,
    fault_id: form.faultId, 
    command_type: form.cmdType, 
    execution_status: form.status, 
    start_time: form.start.replace(' ', 'T'), 
    end_time: form.end ? form.end.replace(' ', 'T') : null, 
    exit_code: form.code 
  }
  
  saving.value = true
  try{
    if (openCreate.value) {
      await LogService.createExecLog(payload)
      ElMessage.success('新增成功')
    } else if (openEditForm.value) {
      if (selected.value === null) return
      await LogService.updateExecLog(selected.value, payload)
      ElMessage.success('更新成功')
    }
    await load()
    dialogVisible.value = false
  }catch(e:any){ 
    ElMessage.error('保存失败：' + (e.friendlyMessage || e.message || '网络错误'))
  } finally {
    saving.value = false
  }
}

async function load(){
  loading.value = true
  try{
    const items = await LogService.listExecLogs()
    const normalized: RecordItem[] = items.map((d:any)=>({
      id: d.id,
      clusterName: d.cluster_name || '',
      username: d.username || d.user_name || d.user?.username || '',
      description: d.description || '',
      faultId: d.fault_id || '',
      cmdType: d.command_type || '',
      status: d.execution_status || 'running',
      start: (d.start_time || '').replace('T',' ').slice(0,19),
      end: d.end_time ? String(d.end_time).replace('T',' ').slice(0,19) : '',
      code: d.exit_code ?? null
    }))
    records.splice(0, records.length, ...normalized)
  }catch(e:any){
    ElMessage.error('加载集群操作日志失败：' + (e.friendlyMessage || e.message || '网络错误'))
    records.splice(0, records.length)
  } finally { 
    loading.value = false 
  }
}

onMounted(()=>{ 
  load() 
  window.addEventListener('resize', updateWidth)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateWidth)
})
</script>

<style scoped>
.exec-logs-container {
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

.w-full {
  width: 100%;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
