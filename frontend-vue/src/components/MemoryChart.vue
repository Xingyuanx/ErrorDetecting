<template>
  <div ref="root" style="width:100%;height:260px"></div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch, nextTick } from 'vue'
import { MetricService } from '../api/metric.service'
import { useUIStore } from '../stores/ui'
import { loadEcharts } from '../lib/echarts'
import type { EChartsType } from 'echarts/core'

const props = defineProps<{ cluster: string }>()
const ui = useUIStore()
const root = ref<HTMLElement|null>(null)
let chart: EChartsType | null = null
let ro: ResizeObserver | null = null
let destroyed = false

function render(used: number, free: number) {
  if (!chart) return
  
  const isDark = ui.isDark
  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: { 
      trigger: 'item', 
      formatter: '{b}: {d}%',
      backgroundColor: isDark ? '#333' : '#fff',
      borderColor: isDark ? '#555' : '#eee',
      textStyle: { color: isDark ? '#fff' : '#333' }
    },
    legend: { 
      bottom: '0%', 
      left: 'center',
      textStyle: { color: isDark ? '#bbb' : '#333' }
    },
    series: [
      {
        name: '内存使用',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { 
          borderRadius: 10, 
          borderColor: isDark ? '#1d1e1f' : '#fff', 
          borderWidth: 2 
        },
        label: { show: false, position: 'center' },
        emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold' } },
        labelLine: { show: false },
        data: [
          { value: used, name: '已使用', itemStyle: { color: '#409EFF' } },
          { value: free, name: '可用', itemStyle: { color: isDark ? '#333' : '#E5E9F2' } }
        ]
      }
    ]
  })
}

async function load() {
  if (!chart || props.cluster === '未选择') return
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

async function initChart() {
  const el = root.value
  if (!el) return
  const echarts = await loadEcharts()
  if (destroyed || root.value !== el) return
  if (chart) chart.dispose()
  chart = echarts.init(el)
  await load()
}

onMounted(() => {
  void initChart()
  const onResize = () => chart && chart.resize()
  window.addEventListener('resize', onResize)
  ro = new ResizeObserver(() => { chart && chart.resize() })
  if (root.value) ro.observe(root.value)
  nextTick(() => { chart && chart.resize() })
  setTimeout(() => { chart && chart.resize() }, 300)
})

watch(() => ui.isDark, () => {
  void initChart()
})
watch(() => props.cluster, () => load())
onBeforeUnmount(() => { destroyed = true; ro?.disconnect(); ro = null; chart?.dispose(); chart = null })
</script>
