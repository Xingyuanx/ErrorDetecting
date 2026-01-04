import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

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
    }
    return response.data // 直接解包 data
  },
  (error) => {
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

    if (status === 401) {
      const auth = useAuthStore()
      auth.logout()
      if (!window.location.hash.includes('login')) {
        window.location.hash = '#/login'
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
