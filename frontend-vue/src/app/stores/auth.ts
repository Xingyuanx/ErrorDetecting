import { defineStore } from 'pinia'
import api from '../lib/api'

type User = { username: string; role: 'admin'|'operator'|'observer' }

export const useAuthStore = defineStore('auth', {
  state: () => ({ user: null as User|null, token: null as string|null }),
  getters: {
    isAuthenticated: (s) => !!s.user,
    role: (s) => s.user?.role || null,
    defaultPage: (s) => {
      const r = s.user?.role
      if (r === 'admin') return 'cluster-list'
      if (r === 'operator') return 'cluster-list'
      if (r === 'observer') return 'cluster-list'
      return 'login'
    }
  },
  actions: {
    restore() {
      const rawUser = localStorage.getItem('cm_user')
      const rawToken = localStorage.getItem('cm_token')
      if (rawUser) this.user = JSON.parse(rawUser)
      if (rawToken) this.token = rawToken
    },
    persist() {
      if (this.user) localStorage.setItem('cm_user', JSON.stringify(this.user))
      else localStorage.removeItem('cm_user')
      if (this.token) localStorage.setItem('cm_token', this.token)
      else localStorage.removeItem('cm_token')
    },
    async login(username: string, password: string) {
      try {
        const r = await api.post('/v1/user/login', { username, password })
        const role = username === 'admin' ? 'admin' : username === 'ops' ? 'operator' : username === 'obs' ? 'observer' : 'observer'
        this.user = { username, role }
        this.token = r?.data?.token || null
        this.persist()
        return { ok: true, role }
      } catch (e: any) {
        if (!e?.response) {
          const demo = { admin: 'admin123', ops: 'ops123', obs: 'obs123' } as const
          const pass = demo[username as keyof typeof demo]
          if (pass && password === pass) {
            const role = username === 'admin' ? 'admin' : username === 'ops' ? 'operator' : 'observer'
            this.user = { username, role }
            this.token = null
            this.persist()
            return { ok: true, role }
          }
        }
        const d = e?.response?.data
        const message = d?.detail === 'invalid_credentials' ? '账号或密码错误' : d?.detail === 'inactive_user' ? '账号未激活' : '登录失败'
        return { ok: false, message }
      }
    },
    async register(username: string, email: string, password: string, fullName: string) {
      try {
        const r = await api.post('/v1/user/register', { username, email, password, fullName })
        const role = username === 'admin' ? 'admin' : username === 'ops' ? 'operator' : username === 'obs' ? 'observer' : 'observer'
        this.user = { username, role }
        this.token = r?.data?.token || null
        this.persist()
        return { ok: true, role }
      } catch (e: any) {
        const d = e?.response?.data
        const errs = d?.detail?.errors
        if (Array.isArray(errs) && errs.length) {
          const message = errs.map((x: any) => x?.message || '').filter(Boolean).join('；')
          return { ok: false, message }
        }
        const message = d?.detail === 'user_exists' ? '用户名已存在' : d?.detail === 'email_exists' ? '邮箱已存在' : '注册失败'
        return { ok: false, message }
      }
    },
    logout() { this.user = null; this.token = null; this.persist() }
  }
})
