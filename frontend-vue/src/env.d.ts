/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

interface ImportMetaEnv {
  readonly VITE_TELEMETRY_ENABLED?: string
  readonly VITE_TELEMETRY_ENDPOINT?: string
  readonly VITE_TELEMETRY_SAMPLE_RATE?: string
  readonly VITE_AUTH_REFRESH_ENABLED?: string
  readonly VITE_AUTH_REFRESH_ENDPOINT?: string
}
