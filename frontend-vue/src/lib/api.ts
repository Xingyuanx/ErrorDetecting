import axios, { type AxiosInstance, type AxiosRequestConfig, type InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '../stores/auth'
import { trackError, trackEvent } from './telemetry'

// 扩展 AxiosInstance 接口，使其支持解包后的数据类型
declare module 'axios' {
  export interface AxiosInstance {
    request<T = any, R = T, D = any>(config: AxiosRequestConfig<D>): Promise<R>;
    get<T = any, R = T, D = any>(url: string, config?: AxiosRequestConfig<D>): Promise<R>;
    delete<T = any, R = T, D = any>(url: string, config?: AxiosRequestConfig<D>): Promise<R>;
    head<T = any, R = T, D = any>(url: string, config?: AxiosRequestConfig<D>): Promise<R>;
    options<T = any, R = T, D = any>(url: string, config?: AxiosRequestConfig<D>): Promise<R>;
    post<T = any, R = T, D = any>(url: string, data?: D, config?: AxiosRequestConfig<D>): Promise<R>;
    put<T = any, R = T, D = any>(url: string, data?: D, config?: AxiosRequestConfig<D>): Promise<R>;
    patch<T = any, R = T, D = any>(url: string, data?: D, config?: AxiosRequestConfig<D>): Promise<R>;
  }
}

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000
})

const refreshApi = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000
})

let refreshPromise: Promise<string | null> | null = null

function isRefreshEnabled() {
  const raw = String(import.meta.env.VITE_AUTH_REFRESH_ENABLED || '')
  if (!raw) return false
  return raw.toLowerCase() === 'true'
}

function getRefreshEndpoint() {
  return String(import.meta.env.VITE_AUTH_REFRESH_ENDPOINT || '/v1/auth/refresh')
}

async function refreshAccessToken() {
  const auth = useAuthStore()
  const refreshToken = auth.refreshToken
  if (!refreshToken) return null
  const endpoint = getRefreshEndpoint()
  const r = await refreshApi.post(endpoint, { refreshToken, refresh_token: refreshToken })
  const token = r?.data?.token || r?.data?.accessToken || r?.data?.access_token || r?.token || r?.accessToken || r?.access_token
  const nextRefresh = r?.data?.refreshToken || r?.data?.refresh_token || r?.refreshToken || r?.refresh_token || refreshToken
  if (!token) return null
  auth.token = token
  auth.refreshToken = nextRefresh || refreshToken
  auth.persist()
  return token as string
}

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const auth = useAuthStore()
    if (auth.token) {
      config.headers.Authorization = `Bearer ${auth.token}`
    }
    // 用于性能监控
    (config as any).metadata = { startTime: new Date() }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    // 性能监控日志
    const startTime = (response.config as any).metadata?.startTime
    if (startTime) {
      const duration = new Date().getTime() - startTime.getTime()
      console.log(`API [${response.config.method?.toUpperCase()}] ${response.config.url} 耗时: ${duration}ms`)
      trackEvent('api_ok', {
        method: response.config.method?.toUpperCase() || '',
        url: String(response.config.url || '').split('?')[0],
        status: response.status,
        durationMs: duration
      })
    }
    return response.data // 直接解包 data
  },
  async (error) => {
    const status = error.response?.status
    const isRegister = error.config?.url?.includes('/v1/user/register')
    let message = '网络异常，请检查您的网络连接'

    if (error.response?.data?.detail) {
      if (typeof error.response.data.detail === 'string') {
        message = error.response.data.detail
      } else {
        message = error.response.data.detail.message || error.response.data.detail.msg || ''
      }
    }

    // 如果最终没有获取到具体错误消息，则拼接状态码
    if (!message) {
      message = isRegister ? `注册请求失败 (状态码: ${status || '未知'})` : '操作失败'
    }

    trackError('api_error', error, {
      method: error.config?.method?.toUpperCase?.() || '',
      url: String(error.config?.url || '').split('?')[0],
      status: status || null
    })

    const shouldTryRefresh =
      status === 401 &&
      isRefreshEnabled() &&
      error?.config &&
      !(error.config as any)._retry &&
      !String(error.config.url || '').includes('/v1/user/login') &&
      !String(error.config.url || '').includes('/v1/user/register') &&
      !String(error.config.url || '').includes(getRefreshEndpoint())

    if (shouldTryRefresh) {
      try {
        (error.config as any)._retry = true
        if (!refreshPromise) {
          refreshPromise = refreshAccessToken().finally(() => {
            refreshPromise = null
          })
        }
        const nextToken = await refreshPromise
        if (nextToken) {
          error.config.headers = error.config.headers || {}
          error.config.headers.Authorization = `Bearer ${nextToken}`
          return api.request(error.config)
        }
      } catch (e) {
        void e
      }
    }

    if (status === 401) {
      const auth = useAuthStore()
      const url = error.config?.url || ''
      // 如果是演示 Token，或者是一些基础检查接口，不触发自动登出
      if (auth.token?.startsWith('demo.') || url.includes('/v1/health') || url.includes('/v1/auth/me')) {
        return Promise.reject({
          ...error,
          friendlyMessage: '鉴权失效 (演示模式或基础接口)'
        })
      }
      const current = window.location.hash.startsWith('#') ? window.location.hash.slice(1) : window.location.hash
      auth.logout()
      if (!window.location.hash.includes('login')) {
        window.location.hash = `#/login?redirect=${encodeURIComponent(current || '/diagnosis')}`
      }
    }

    // 可以在这里扩展更多的状态码处理
    return Promise.reject({
      ...error,
      friendlyMessage: message
    })
  }
)

export default api
