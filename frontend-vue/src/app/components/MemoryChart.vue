<template>
  <div ref="root" style="height:260px"></div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref } from 'vue'
import * as echarts from 'echarts'
const root = ref<HTMLElement|null>(null)
let chart: echarts.ECharts | null = null
onMounted(() => {
  if (!root.value) return
  chart = echarts.init(root.value)
  chart.setOption({ series: [{ type: 'pie', radius: ['40%','70%'], data: [{ value: 8.5, name: '已使用' }, { value: 15.5, name: '可用' }] }] })
  const onResize = () => chart && chart.resize()
  window.addEventListener('resize', onResize)
})
onBeforeUnmount(() => { chart?.dispose(); chart = null })
</script>

