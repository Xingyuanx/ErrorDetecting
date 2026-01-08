import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const target = env.VITE_API_TARGET || "http://localhost:8000";
  const devHost = env.VITE_DEV_HOST || "0.0.0.0";
  const devPort = 5173;
  const hmrHost = "localhost";
  const hmrPort = 5173;
  const allowedHostsEnv = (env.VITE_ALLOWED_HOSTS || "").split(",").map((s) => s.trim()).filter(Boolean);
  const isProd = mode === "production";
  return {
    plugins: [vue()],
    cacheDir: ".vite",
    esbuild: isProd ? { drop: ["console", "debugger"] } : undefined,
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            vue: ["vue", "vue-router", "pinia"],
            elementPlus: ["element-plus"],
            vendor: ["axios", "@vueuse/core", "marked", "vue-i18n"],
          },
        },
      },
    },
    server: {
      host: devHost,
      strictPort: true,
      port: devPort,
      // 完全关闭 HMR 以屏蔽 HMR 客户端的探测报错
      hmr: false,
      cors: true,
      allowedHosts: allowedHostsEnv.length ? allowedHostsEnv : true,
      proxy: {
        "/api": {
          target,
          changeOrigin: true,
          timeout: 200000, // 代理请求超时设置为 200s (略大于业务超时 180s)
          proxyTimeout: 200000, // 代理响应超时设置为 200s
        },
      },
    },
  };
});
