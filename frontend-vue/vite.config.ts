import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const target = env.VITE_API_TARGET || "http://localhost:8000";
  const devHost = env.VITE_DEV_HOST || "0.0.0.0";
  const devPort = Number(env.VITE_DEV_PORT || 5173);
  const hmrHost = env.VITE_HMR_HOST || devHost;
  const hmrPort = Number(env.VITE_HMR_PORT || devPort);
  const allowedHostsEnv = (env.VITE_ALLOWED_HOSTS || "").split(",").map((s) => s.trim()).filter(Boolean);
  return {
    plugins: [vue()],
    server: {
      host: devHost,
      strictPort: true,
      port: devPort,
      hmr: {
        host: hmrHost,
        clientPort: hmrPort,
      },
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
