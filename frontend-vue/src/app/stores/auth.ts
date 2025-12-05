import { defineStore } from 'pinia'

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
    login(username: string, password: string) {
      const demo = {
        admin: { u: 'admin', p: 'admin123', role: 'admin' },
        ops: { u: 'ops', p: 'ops123', role: 'operator' },
        obs: { u: 'obs', p: 'obs123', role: 'observer' }
      } as const
      const m = Object.values(demo).find(d => d.u === username && d.p === password)
      if (!m) return { ok: false, message: '账号或密码错误' }
      this.user = { username, role: m.role }
      this.persist()
      return { ok: true, role: m.role }
    },
    logout() { this.user = null; this.persist() }
  }
})

