import api from '../lib/api'
import type { Cluster, ClusterRegisterPayload } from '../types'

export const ClusterService = {
  /** 获取所有集群列表 */
  async list(): Promise<Cluster[]> {
    const res = await api.get<{ clusters: Cluster[] }>('/v1/clusters')
    return res.clusters || []
  },

  /** 注册集群 */
  async register(payload: ClusterRegisterPayload): Promise<any> {
    return api.post('/v1/clusters', payload)
  },

  /** 注销集群 */
  async unregister(id: string): Promise<any> {
    return api.delete(`/v1/clusters/${encodeURIComponent(id)}`)
  },

  /** 启动集群 */
  async start(id: string): Promise<{ status: string; logs: string[] }> {
    return api.post(`/v1/ops/clusters/${encodeURIComponent(id)}/start`, {}, { timeout: 60000 })
  },

  /** 停止集群 */
  async stop(id: string): Promise<{ status: string; logs: string[] }> {
    return api.post(`/v1/ops/clusters/${encodeURIComponent(id)}/stop`, {}, { timeout: 60000 })
  }
}
