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
  chart.setOption({ xAxis: { type: 'category', boundaryGap: false, data: ['00:00','04:00','08:00','12:00','16:00','20:00','24:00'] }, yAxis: { type: 'value', min:0, max:100 }, series: [{ type: 'line', smooth: true, data: [20,35,45,60,55,40,30] }] })
  const onResize = () => chart && chart.resize()
  window.addEventListener('resize', onResize)
})
onBeforeUnmount(() => { chart?.dispose(); chart = null })
</script>

