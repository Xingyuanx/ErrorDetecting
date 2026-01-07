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

  /** 立即采样 CPU/内存 指标 (旧接口，保留兼容) */
  async sampleMetrics(clusterUuid: string): Promise<any> {
    return api.post(`/v1/metrics/${clusterUuid}/`, null, {
      timeout: 180000 
    })
  },

  /** 启动集群后台采集器 */
  async startCollector(clusterUuid: string, interval: number = 5): Promise<any> {
    return api.post(`/v1/metrics/collectors/start-by-cluster/${clusterUuid}`, null, {
      params: { interval }
    })
  },

  /** 获取采集器状态 */
  async getCollectorStatus(clusterUuid?: string): Promise<{ 
    is_running: boolean, 
    active_collectors_count: number, 
    interval: number, 
    collectors: Record<string, string>, 
    errors: Record<string, string> 
  }> {
    return api.get(`/v1/metrics/collectors/status`, { params: { cluster: clusterUuid } })
  },

  /** 停止集群后台采集器 */
  async stopCollector(clusterUuid: string): Promise<any> {
    return api.post(`/v1/metrics/collectors/stop-by-cluster/${clusterUuid}`)
  }
}
