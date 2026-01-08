<template>
  <div class="login-container">
    <div class="theme-toggle-wrapper">
      <el-button link @click="toggleThemeWithAnimation" class="theme-toggle-btn">
        <el-icon :size="24">
          <Moon v-if="!isDark" />
          <Sunny v-else />
        </el-icon>
      </el-button>
    </div>
    <el-card class="login-card">
      <div class="login-header">
        <el-icon :size="48" color="#0ea5e9"><Monitor /></el-icon>
        <h1 class="login-title">集群管理系统</h1>
        <p class="login-subtitle">请登录您的账号以继续</p>
      </div>

      <el-form
        :model="loginForm"
        :rules="rules"
        ref="loginFormRef"
        label-position="top"
        @submit.prevent="onSubmit"
        size="large"
      >
        <el-form-item label="账号" prop="username">
          <el-input
            v-model.trim="loginForm.username"
            placeholder="请输入账号"
            prefix-icon="User"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model.trim="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            class="submit-btn"
            :loading="loading"
            native-type="submit"
          >
            登录
          </el-button>
        </el-form-item>

        <div class="register-link">
          还没有账号？
          <el-link type="primary" @click="router.push('/register')">立即注册</el-link>
        </div>
      </el-form>

      <div class="health-status">
        <el-tag :type="health === 'ok' ? 'success' : health === 'fail' ? 'danger' : 'info'" size="small">
          后端连接：{{ health === 'ok' ? '正常' : health === 'fail' ? '异常' : '检测中' }}
        </el-tag>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import { useAuthStore } from "../stores/auth";
import { useUIStore } from "../stores/ui";
import { AuthService } from "../api/auth.service";
import { ElMessage } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import { Monitor, User, Lock, Moon, Sunny } from '@element-plus/icons-vue'

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();
const ui = useUIStore();
const { isDark } = storeToRefs(ui);
const loginFormRef = ref<FormInstance>();
const loading = ref(false);
const health = ref<"ok" | "fail" | "checking">("checking");

function toggleThemeWithAnimation(event: MouseEvent) {
  const isAppearanceTransition = (document as any).startViewTransition &&
    !window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (!isAppearanceTransition) {
    ui.toggleTheme();
    return;
  }

  const x = event.clientX;
  const y = event.clientY;
  const endRadius = Math.hypot(
    Math.max(x, innerWidth - x),
    Math.max(y, innerHeight - y)
  );

  const transition = (document as any).startViewTransition(async () => {
    ui.toggleTheme();
  });

  transition.ready.then(() => {
    const clipPath = [
      `circle(0px at ${x}px ${y}px)`,
      `circle(${endRadius}px at ${x}px ${y}px)`,
    ];
    document.documentElement.animate(
      {
        clipPath: isDark.value ? [...clipPath].reverse() : clipPath,
      },
      {
        duration: 450,
        easing: 'ease-in-out',
        pseudoElement: isDark.value
          ? '::view-transition-old(root)'
          : '::view-transition-new(root)',
      }
    );
  });
}

const loginForm = reactive({
  username: "",
  password: ""
});

const rules = reactive<FormRules>({
  username: [{ required: true, message: "请输入账号", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }]
});

onMounted(async () => {
  try {
    await AuthService.health();
    health.value = "ok";
  } catch {
    health.value = "fail";
  }
});

async function onSubmit() {
  if (!loginFormRef.value) return;
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        const r = await auth.login(loginForm.username, loginForm.password);
        if (r.ok) {
          ElMessage.success("登录成功");
          const redirect = typeof route.query.redirect === "string" ? route.query.redirect : "";
          router.replace(redirect || { name: auth.defaultPage });
        } else {
          ElMessage.error(r.message || "登录失败！");
        }
      } finally {
        loading.value = false;
      }
    }
  });
}
</script>

<style scoped>
.login-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
}

.theme-toggle-wrapper {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 10;
}

.login-card {
  width: 100%;
  max-width: 400px;
  border-radius: 12px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--app-border-color);
  background: var(--app-card-bg);
}

:deep(.el-card__body) {
  padding: 24px 40px;
}

.login-header {
  text-align: center;
  margin-bottom: 20px;
}

.login-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--app-text-primary);
  margin: 12px 0 4px;
}

.login-subtitle {
  font-size: 14px;
  color: var(--app-text-secondary);
}

:deep(.el-form-item) {
  margin-bottom: 16px;
}

.submit-btn {
  width: 100%;
  height: 40px;
  font-size: 16px;
  font-weight: 600;
}

.register-link {
  text-align: center;
  font-size: 14px;
  color: var(--app-text-secondary);
  margin-top: 8px;
}

.health-status {
  text-align: center;
  margin-top: 20px;
}
</style>
