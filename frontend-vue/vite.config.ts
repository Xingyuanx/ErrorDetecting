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
  return {
    plugins: [vue()],
    cacheDir: ".vite",
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
        },
      },
    },
  };
});
