import api from '../lib/api'

export const UserService = {
  /** 获取用户列表 */
  async list(): Promise<any[]> {
    const res = await api.get<any>('/v1/users')
    return res.users || res
  },

  /** 创建用户 */
  async create(payload: any): Promise<any> {
    return api.post('/v1/users', payload)
  },

  /** 更新用户信息 */
  async update(username: string, payload: any): Promise<any> {
    return api.patch(`/v1/users/${encodeURIComponent(username)}`, payload)
  },

  /** 删除用户 */
  async remove(username: string): Promise<any> {
    return api.delete(`/v1/users/${encodeURIComponent(username)}`)
  },

  /** 修改当前用户密码 */
  async updatePassword(payload: any): Promise<any> {
    return api.patch('/v1/user/password', payload)
  }
}
