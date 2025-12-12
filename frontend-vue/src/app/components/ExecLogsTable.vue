<template>
  <table class="dashboard__table">
    <thead>
      <tr>
        <th>执行ID</th>
        <th>故障ID</th>
        <th>命令类型</th>
        <th>状态</th>
        <th>开始时间</th>
        <th>结束时间</th>
        <th>退出码</th>
        <th>操作</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="r in records" :key="r.id" class="dashboard__table-row" :class="{ 'row--selected': selectedId===r.id }" @click="$emit('select', r)">
        <td>{{ r.id }}</td>
        <td>{{ r.faultId }}</td>
        <td>{{ r.cmdType }}</td>
        <td><span :class="statusClass(r.status)">{{ r.status }}</span></td>
        <td>{{ r.start }}</td>
        <td>{{ r.end || '-' }}</td>
        <td>{{ r.code ?? '-' }}</td>
        <td>
          <button class="btn u-text-sm" type="button" @click.stop="$emit('edit', r)">编辑</button>
          <button class="btn u-text-sm u-ml-1" type="button" @click.stop="$emit('delete', r.id)">删除</button>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
type RecordItem = { id:string; faultId:string; cmdType:string; status:'running'|'success'|'failed'; start:string; end:string|''; code:number|null }
defineProps<{ records: RecordItem[]; selectedId: string }>()
function statusClass(s:'running'|'success'|'failed'){ return s==='running'?'status--running': s==='success'?'status--success':'status--failed' }
</script>

<style scoped>
.row--selected{ background:#eef2ff }
.status--running{ color:#2563eb }
.status--success{ color:#16a34a }
.status--failed{ color:#dc2626 }
</style>
