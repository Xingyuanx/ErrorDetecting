import { defineStore } from 'pinia'
import axios from 'axios'
const api = axios.create({ baseURL: '/api' })

type User = { username: string; role: 'admin'|'operator'|'observer' }

export const useAuthStore = defineStore('auth', {
  state: () => ({ user: null as User|null }),
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
      const raw = localStorage.getItem('cm_user')
      if (raw) this.user = JSON.parse(raw)
    },
    persist() {
      if (this.user) localStorage.setItem('cm_user', JSON.stringify(this.user))
      else localStorage.removeItem('cm_user')
    },
    async login(username: string, password: string) {
      try {
        const r = await api.post('/v1/user/login', { username, password })
        const role = username === 'admin' ? 'admin' : username === 'ops' ? 'operator' : username === 'obs' ? 'observer' : 'observer'
        this.user = { username, role }
        this.persist()
        return { ok: true, role }
      } catch (e: any) {
        if (!e?.response) {
          const demo = { admin: 'admin123', ops: 'ops123', obs: 'obs123' } as const
          const pass = demo[username as keyof typeof demo]
          if (pass && password === pass) {
            const role = username === 'admin' ? 'admin' : username === 'ops' ? 'operator' : 'observer'
            this.user = { username, role }
            this.persist()
            return { ok: true, role }
          }
        }
        const d = e?.response?.data
        const message = d?.detail === 'invalid_credentials' ? '账号或密码错误' : d?.detail === 'inactive_user' ? '账号未激活' : '登录失败'
        return { ok: false, message }
      }
    },
    logout() { this.user = null; this.persist() }
  }
})
