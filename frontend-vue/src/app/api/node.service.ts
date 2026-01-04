import api from '../lib/api'
import type { Node } from '../types'

export const NodeService = {
  /** 获取指定集群的节点列表 */
  async listByCluster(clusterId: string): Promise<Node[]> {
    const res = await api.get<{ nodes: Node[] }>(`/v1/nodes`, { params: { cluster: clusterId } })
    return res.nodes || []
  },

  /** 启动节点 */
  async start(name: string): Promise<any> {
    return api.post(`/v1/nodes/${encodeURIComponent(name)}/start`)
  },

  /** 停止节点 */
  async stop(name: string): Promise<any> {
    return api.post(`/v1/nodes/${encodeURIComponent(name)}/stop`)
  },

  /** 删除节点 */
  async remove(name: string): Promise<any> {
    return api.delete(`/v1/nodes/${encodeURIComponent(name)}`)
  },

  /** 获取节点详情 */
  async getDetail(name: string): Promise<any> {
    return api.get(`/v1/nodes/${encodeURIComponent(name)}`)
  }
}
