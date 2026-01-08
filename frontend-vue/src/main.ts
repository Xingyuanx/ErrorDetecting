import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import './styles/theme.scss'
import { Aim, ArrowDown, ArrowRight, CircleCheck, Edit, Expand, Fold, FullScreen, Lock, Monitor, Moon, More, Plus, Rank, Refresh, Sunny, User, UserFilled, Message } from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import { initTelemetry, installGlobalErrorHandlers, trackEvent } from './lib/telemetry'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)

app.component('Aim', Aim)
app.component('ArrowDown', ArrowDown)
app.component('ArrowRight', ArrowRight)
app.component('CircleCheck', CircleCheck)
app.component('Edit', Edit)
app.component('Expand', Expand)
app.component('Fold', Fold)
app.component('FullScreen', FullScreen)
app.component('Lock', Lock)
app.component('Monitor', Monitor)
app.component('Moon', Moon)
app.component('More', More)
app.component('Plus', Plus)
app.component('Rank', Rank)
app.component('Refresh', Refresh)
app.component('Sunny', Sunny)
app.component('User', User)
app.component('UserFilled', UserFilled)
app.component('Message', Message)

app.use(ElementPlus)
const auth = useAuthStore()
auth.restore()
app.use(router)
initTelemetry({
  enabled: String(import.meta.env.VITE_TELEMETRY_ENABLED || '').toLowerCase() === 'true',
  endpoint: String(import.meta.env.VITE_TELEMETRY_ENDPOINT || ''),
  sampleRate: Number(import.meta.env.VITE_TELEMETRY_SAMPLE_RATE || 1),
  getContext: () => ({
    route: window.location.hash || '',
    userId: auth.user?.id || null,
    role: auth.user?.role || null
  })
})
installGlobalErrorHandlers()
trackEvent('app_boot')
app.mount('#app')
