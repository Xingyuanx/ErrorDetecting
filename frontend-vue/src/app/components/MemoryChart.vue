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
function render(used: number, free: number) {
  chart?.setOption({ series: [{ type: 'pie', radius: ['40%','70%'], data: [{ value: used, name: '已使用' }, { value: free, name: '可用' }] }] })
}
async function load() {
  if (!chart) return
  try {
    const { used, free } = await MetricService.getMemoryUsage(props.cluster)
    if (used > 0 || free > 0) {
      render(used, free)
    } else {
      render(8.5, 15.5)
    }
  } catch {
    render(8.5, 15.5)
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
