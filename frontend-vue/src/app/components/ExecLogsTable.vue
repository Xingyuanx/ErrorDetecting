<template>
  <el-table
    :data="records"
    stripe
    style="width: 100%"
    header-cell-class-name="table-header"
    highlight-current-row
    @current-change="handleCurrentChange"
  >
    <el-table-column prop="id" label="ID" width="80" />
    <el-table-column prop="clusterName" label="集群" width="150" show-overflow-tooltip />
    <el-table-column prop="username" label="用户" width="120" />
    <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
    <el-table-column label="状态" width="120">
      <template #default="{ row }">
        <el-tag :type="statusType(row.status)" size="small" effect="light">
          {{ row.status }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="start" label="开始时间" width="180" />
    <el-table-column label="结束时间" width="180">
      <template #default="{ row }">
        {{ row.end || '-' }}
      </template>
    </el-table-column>
    <el-table-column label="操作" width="100" fixed="right">
      <template #default="{ row }">
        <el-popconfirm title="确定要删除这条记录吗？" @confirm="$emit('delete', row.id)">
          <template #reference>
            <el-button size="small" type="danger" plain @click.stop>删除</el-button>
          </template>
        </el-popconfirm>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup lang="ts">
type RecordItem = { id:number; clusterName:string; username:string; description:string; faultId:string; cmdType:string; status:'running'|'success'|'failed'; start:string; end:string|''; code:number|null }
const props = defineProps<{ records: RecordItem[]; selectedId: number | null }>()
const emit = defineEmits(['select', 'delete'])

function statusType(s: 'running' | 'success' | 'failed') {
  const map: Record<string, string> = {
    'running': 'primary',
    'success': 'success',
    'failed': 'danger'
  }
  return map[s] || 'info'
}

function handleCurrentChange(val: RecordItem | null) {
  if (val) emit('select', val)
}
</script>

<style scoped>
:deep(.table-header) {
  background-color: #f8fafc !important;
  color: #475569;
  font-weight: 600;
}
</style>
