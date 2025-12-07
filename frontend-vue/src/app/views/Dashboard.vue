<template>
  <section class="layout__section">
    <div class="layout__page-header"><h2 class="layout__page-title">仪表板</h2></div>
    <div class="u-mb-2">
      <div>当前集群 UUID：{{ meta.uuid }}</div>
      <div>Master 主机：{{ meta.host }}</div>
      <div>Master IP：{{ meta.ip }}</div>
    </div>
    <div class="grid grid-cols-2 gap-4">
      <div><CpuChart /></div>
      <div><MemoryChart /></div>
    </div>
</section>
</template>

<script setup lang="ts">
import { onMounted, reactive } from 'vue'
import CpuChart from '../components/CpuChart.vue'
import MemoryChart from '../components/MemoryChart.vue'
const meta = reactive({ uuid: '未选择', host: '-', ip: '-' })
onMounted(() => {
  const raw = sessionStorage.getItem('current_cluster')
  if (raw) Object.assign(meta, JSON.parse(raw))
})
</script>
