import api from '../lib/api'

export const AuthService = {
  /** 登录 */
  async login(payload: any): Promise<any> {
    return api.post('/v1/user/login', payload)
  },

  /** 注册 */
  async register(payload: any): Promise<any> {
    return api.post('/v1/user/register', payload)
  },

  /** 获取当前用户信息 */
  async me(): Promise<any> {
    return api.get('/v1/auth/me')
  },

  /** 后端健康检查 */
  async health(): Promise<any> {
    return api.get('/v1/health')
  }
}
