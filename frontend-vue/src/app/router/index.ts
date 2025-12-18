import { createRouter, createWebHashHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { Roles, AllRoles } from '../constants/roles'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/cluster-list' },
  { path: '/login', name: 'login', component: () => import('../views/Login.vue'), meta: { requiresAuth: false, hideSidebar: true } },
  { path: '/register', name: 'register', component: () => import('../views/Register.vue'), meta: { requiresAuth: false, hideSidebar: true } },
  { path: '/cluster-list', name: 'cluster-list', component: () => import('../views/ClusterList.vue'), meta: { requiresAuth: true, roles: AllRoles } },
  { path: '/dashboard', name: 'dashboard', component: () => import('../views/Dashboard.vue'), meta: { requiresAuth: true, roles: AllRoles } },
  { path: '/logs', name: 'logs', component: () => import('../views/Logs.vue'), meta: { requiresAuth: true, roles: AllRoles } },
  { path: '/diagnosis', name: 'diagnosis', component: () => import('../views/Diagnosis.vue'), meta: { requiresAuth: true, roles: [Roles.admin, Roles.operator] } },
  { path: '/exec-logs', name: 'exec-logs', component: () => import('../views/ExecLogs.vue'), meta: { requiresAuth: true, roles: AllRoles } },
  { path: '/alert-config', name: 'alert-config', component: () => import('../views/AlertConfig.vue'), meta: { requiresAuth: true, roles: [Roles.admin, Roles.operator] } },
  { path: '/profile', name: 'profile', component: () => import('../views/Profile.vue'), meta: { requiresAuth: true, roles: AllRoles } },
  { path: '/account', name: 'account', component: () => import('../views/Account.vue'), meta: { requiresAuth: true, roles: AllRoles } },
  { path: '/user-management', name: 'user-management', component: () => import('../views/UserManagement.vue'), meta: { requiresAuth: true, roles: [Roles.admin] } },
  { path: '/audit-logs', name: 'audit-logs', component: () => import('../views/AuditLogs.vue'), meta: { requiresAuth: true, roles: [Roles.admin] } }
]

const router = createRouter({ history: createWebHashHistory(), routes })

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta || to.meta.requiresAuth === false) return true
  if (!auth.isAuthenticated) return { name: 'login' }
  const roles = to.meta.roles as string[] | undefined
  if (roles && !roles.includes(auth.role || '')) return { name: auth.defaultPage }
  return true
})

export default router
