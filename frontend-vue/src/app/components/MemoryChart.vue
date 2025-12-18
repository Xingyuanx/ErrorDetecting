<template>
  <div ref="root" style="width:100%;height:260px"></div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import api from '../lib/api'
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
    const r = await api.get('/v1/metrics/memory_usage', { params: { cluster: props.cluster }, headers: auth.token ? { Authorization: `Bearer ${auth.token}` } : undefined })
    const used = Number(r.data?.used ?? 8.5)
    const free = Number(r.data?.free ?? 15.5)
    render(used, free)
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
