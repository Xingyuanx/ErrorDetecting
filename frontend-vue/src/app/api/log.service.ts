import api from '../lib/api'

export const LogService = {
  /** 获取日志列表 */
  async list(params: any): Promise<{ items: any[], total: number }> {
    const res = await api.get<any>('/v1/logs', { params })
    const items = Array.isArray(res?.items) ? res.items : (Array.isArray(res?.logs) ? res.logs : [])
    const total = Number(res?.total ?? items.length)
    return { items, total }
  },

  /** 获取系统操作日志 */
  async listOperationLogs(): Promise<any[]> {
    const res = await api.get<any>('/v1/sys-exec-logs')
    return Array.isArray(res?.items) ? res.items : (Array.isArray(res?.operation_logs) ? res.operation_logs : [])
  },

  /** 获取集群执行日志 */
  async listExecLogs(): Promise<any[]> {
    const res = await api.get<any>('/v1/exec-logs')
    return Array.isArray(res?.items) ? res.items : (Array.isArray(res?.logs) ? res.logs : [])
  },

  /** 创建执行日志 */
  async createExecLog(payload: any): Promise<any> {
    return api.post('/v1/exec-logs', payload)
  },

  /** 更新执行日志 */
  async updateExecLog(id: number, payload: any): Promise<any> {
    return api.put(`/v1/exec-logs/${id}`, payload)
  },

  /** 删除执行日志 */
  async removeExecLog(id: number): Promise<any> {
    return api.delete(`/v1/exec-logs/${id}`)
  }
}
