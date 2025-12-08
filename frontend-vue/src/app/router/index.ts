import { createRouter, createWebHashHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/cluster-list' },
  { path: '/login', name: 'login', component: () => import('../views/Login.vue'), meta: { requiresAuth: false } },
  { path: '/register', name: 'register', component: () => import('../views/Register.vue'), meta: { requiresAuth: false } },
  { path: '/cluster-list', name: 'cluster-list', component: () => import('../views/ClusterList.vue'), meta: { requiresAuth: true, roles: ['admin','operator','observer'] } },
  { path: '/dashboard', name: 'dashboard', component: () => import('../views/Dashboard.vue'), meta: { requiresAuth: true, roles: ['admin','operator','observer'] } },
  { path: '/logs', name: 'logs', component: () => import('../views/Logs.vue'), meta: { requiresAuth: true, roles: ['admin','operator','observer'] } },
  { path: '/diagnosis', name: 'diagnosis', component: () => import('../views/Diagnosis.vue'), meta: { requiresAuth: true, roles: ['admin','operator'] } },
  { path: '/fault-center', name: 'fault-center', component: () => import('../views/FaultCenter.vue'), meta: { requiresAuth: true, roles: ['admin','operator','observer'] } },
  { path: '/exec-logs', name: 'exec-logs', component: () => import('../views/ExecLogs.vue'), meta: { requiresAuth: true, roles: ['admin','operator','observer'] } },
  { path: '/alert-config', name: 'alert-config', component: () => import('../views/AlertConfig.vue'), meta: { requiresAuth: true, roles: ['admin','operator'] } },
  { path: '/profile', name: 'profile', component: () => import('../views/Profile.vue'), meta: { requiresAuth: true, roles: ['admin','operator','observer'] } },
  { path: '/account', name: 'account', component: () => import('../views/Account.vue'), meta: { requiresAuth: true, roles: ['admin','operator','observer'] } },
  { path: '/user-management', name: 'user-management', component: () => import('../views/UserManagement.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/role-assignment', name: 'role-assignment', component: () => import('../views/RoleAssignment.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/permission-policy', name: 'permission-policy', component: () => import('../views/PermissionPolicy.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/audit-logs', name: 'audit-logs', component: () => import('../views/AuditLogs.vue'), meta: { requiresAuth: true, roles: ['admin'] } }
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

