import { defineStore } from 'pinia'
import { AuthService } from '../api/auth.service'

type User = { id: number; username: string; role: 'admin'|'operator'|'observer' }

function makeDemoToken() {
  const payload = { sub: 'demo-admin', role: 'admin', iat: Date.now(), exp: Date.now() + 12 * 60 * 60 * 1000 }
  const body = typeof btoa === 'function' ? btoa(JSON.stringify(payload)) : JSON.stringify(payload)
  return `demo.${body}.${Math.random().toString(36).slice(2)}`
}

function normalizeRole(r: string): 'admin'|'operator'|'observer'|'' {
  const v = String(r || '').trim().toLowerCase()
  if (!v) return ''
  if (v === 'admin' || v === 'administrator') return 'admin'
  if (v === 'operator' || v === 'ops' || v === 'op') return 'operator'
  if (v === 'observer' || v === 'obs' || v === 'view') return 'observer'
  return ''
}

export const useAuthStore = defineStore('auth', {
  state: () => ({ user: null as User|null, token: null as string|null, refreshToken: null as string|null }),
  getters: {
    isAuthenticated: (s) => !!(s.user && s.token),
    role: (s) => s.user?.role || null,
    defaultPage: (s) => {
      const r = s.user?.role
      if (r === 'admin' || r === 'operator') return 'diagnosis'
      if (r === 'observer') return 'cluster-list'
      return 'login'
    }
  },
  actions: {
    restore() {
      const rawUser = localStorage.getItem('cm_user')
      const rawToken = localStorage.getItem('cm_token')
      const rawRefreshToken = localStorage.getItem('cm_refresh_token')
      if (rawUser && rawToken) {
        this.user = JSON.parse(rawUser)
        this.token = rawToken
        this.refreshToken = rawRefreshToken || null
      } else {
        this.user = null
        this.token = null
        this.refreshToken = null
        localStorage.removeItem('cm_user')
        localStorage.removeItem('cm_token')
        localStorage.removeItem('cm_refresh_token')
      }
    },
    persist() {
      if (this.user) localStorage.setItem('cm_user', JSON.stringify(this.user))
      else localStorage.removeItem('cm_user')
      if (this.token) localStorage.setItem('cm_token', this.token)
      else localStorage.removeItem('cm_token')
      if (this.refreshToken) localStorage.setItem('cm_refresh_token', this.refreshToken)
      else localStorage.removeItem('cm_refresh_token')
    },
    async login(username: string, password: string) {
      try {
        // 特例处理演示账号：账号密码均为 123 时，直接以管理员身份登录
        if (username === '123' && password === '123') {
          const token = makeDemoToken()
          this.user = { id: 888, username: 'demo-admin', role: 'admin' }
          this.token = token
          this.refreshToken = 'demo-refresh-token'
          this.persist()
          return { ok: true, role: 'admin' }
        }

        const r: any = await AuthService.login({ username, password })
        const token = r?.token
        const refreshToken = r?.refreshToken || r?.refresh_token || r?.tokens?.refresh || null
        const userId = r?.user?.id || r?.id || 0
        const backendRoles = (r?.roles || []) as string[]
        const backendRoleRaw = (r?.user?.role || r?.role || r?.role_key || (backendRoles.length > 0 ? backendRoles[0] : '')) as string
        const backendRole = normalizeRole(backendRoleRaw)
        const role: 'admin'|'operator'|'observer' = backendRole || (username === 'admin' || username === 'administrator' ? 'admin' : (username === 'ops' || username === 'operator') ? 'operator' : 'observer')
        if (!token) {
          return { ok: false, message: '登录失败' }
        }
        this.user = { id: userId, username, role }
        this.token = token
        this.refreshToken = refreshToken
        this.persist()
        return { ok: true, role }
      } catch (e: any) {
        return { ok: false, message: e.friendlyMessage || '登录失败' }
      }
    },
    async register(username: string, email: string, password: string, fullName: string) {
      try {
        const r: any = await AuthService.register({ username, email, password, fullName })
        const userId = r?.user?.id || r?.id || 0
        const backendRoles = (r?.roles || []) as string[]
        const backendRoleRaw = (r?.user?.role || r?.role || r?.role_key || (backendRoles.length > 0 ? backendRoles[0] : '')) as string
        const backendRole = normalizeRole(backendRoleRaw)
        const role: 'admin'|'operator'|'observer' = backendRole || (username === 'admin' || username === 'administrator' ? 'admin' : (username === 'ops' || username === 'operator') ? 'operator' : 'observer')
        this.user = { id: userId, username, role }
        this.token = r?.token || null
        this.refreshToken = r?.refreshToken || r?.refresh_token || r?.tokens?.refresh || null
        this.persist()
        return { ok: true, role }
      } catch (e: any) {
        return { ok: false, message: e.friendlyMessage || '注册失败' }
      }
    },
    logout() { 
      // 如果是演示账号，忽略来自 API 拦截器的登出请求，防止在后端异常时被强制踢出
      if (this.token?.startsWith('demo.')) {
        return
      }
      this.user = null; 
      this.token = null; 
      this.refreshToken = null; 
      this.persist() 
    }
  }
})
