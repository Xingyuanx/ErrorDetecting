import api from '../lib/api'

export const MetricService = {
  /** 获取 CPU 趋势数据 */
  async getCpuTrend(cluster: string): Promise<{ times: string[], values: number[] }> {
    const res = await api.get<any>('/v1/metrics/cpu_trend', { params: { cluster } })
    return {
      times: Array.isArray(res?.times) ? res.times : [],
      values: Array.isArray(res?.values) ? res.values : []
    }
  },

  /** 获取内存使用情况 */
  async getMemoryUsage(cluster: string): Promise<{ used: number, free: number }> {
    const res = await api.get<any>('/v1/metrics/memory_usage', { params: { cluster } })
    return {
      used: Number(res?.used ?? 0),
      free: Number(res?.free ?? 0)
    }
  },

  /** 立即采样 CPU/内存 指标 */
  async sampleMetrics(clusterUuid: string): Promise<any> {
    return api.post(`/v1/metrics/${clusterUuid}/`)
  }
}
