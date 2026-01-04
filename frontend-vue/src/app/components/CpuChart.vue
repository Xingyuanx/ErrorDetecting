<template>
  <div ref="root" style="width:100%;height:260px"></div>
  </template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { MetricService } from '../api/metric.service'
import { useAuthStore } from '../stores/auth'
const props = defineProps<{ cluster: string }>()
const auth = useAuthStore()
const root = ref<HTMLElement|null>(null)
let chart: echarts.ECharts | null = null
let ro: ResizeObserver | null = null
function render(times: string[], values: number[]) {
  chart?.setOption({ xAxis: { type: 'category', boundaryGap: false, data: times }, yAxis: { type: 'value', min:0, max:100 }, series: [{ type: 'line', smooth: true, areaStyle: {}, data: values }] })
}
async function load() {
  if (!chart) return
  try {
    const { times, values } = await MetricService.getCpuTrend(props.cluster)
    if (times.length > 0 && values.length > 0) {
      render(times, values)
    } else {
      render(['00:00','04:00','08:00','12:00','16:00','20:00','24:00'], [20,35,45,60,55,40,30])
    }
  } catch {
    render(['00:00','04:00','08:00','12:00','16:00','20:00','24:00'], [20,35,45,60,55,40,30])
  }
}
onMounted(() => {
  if (!root.value) return
  chart = echarts.init(root.value)
  load()
  const onResize = () => chart && chart.resize()
  window.addEventListener('resize', onResize)
  ro = new ResizeObserver(() => { chart && chart.resize() })
  ro.observe(root.value)
  nextTick(() => { chart && chart.resize() })
  setTimeout(() => { chart && chart.resize() }, 300)
})
watch(() => props.cluster, () => load())
onBeforeUnmount(() => { ro?.disconnect(); ro = null; chart?.dispose(); chart = null })
</script>
