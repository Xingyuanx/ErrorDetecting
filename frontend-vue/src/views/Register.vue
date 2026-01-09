<template>
  <div class="register-container">
    <div class="theme-toggle-wrapper">
      <el-button link @click="toggleThemeWithAnimation" class="theme-toggle-btn">
        <el-icon :size="24">
          <Moon v-if="!isDark" />
          <Sunny v-else />
        </el-icon>
      </el-button>
    </div>
    <el-card class="register-card">
      <div class="register-header">
        <el-icon :size="48" color="#0ea5e9"><User /></el-icon>
        <h2 class="register-title">新用户注册</h2>
        <p class="register-subtitle">填写以下信息完成账号注册</p>
      </div>

      <el-form
        :model="registerForm"
        :rules="rules"
        ref="registerFormRef"
        label-position="top"
        @submit.prevent="onSubmit"
        size="large"
      >
        <el-form-item label="账号" prop="username">
          <el-input
            v-model.trim="registerForm.username"
            placeholder="请输入账号"
            prefix-icon="User"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model.trim="registerForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
          />
          <div class="form-tip">需至少8位，包含大小写字母和数字</div>
        </el-form-item>

        <el-form-item label="确认密码" prop="confirm">
          <el-input
            v-model.trim="registerForm.confirm"
            type="password"
            placeholder="请再次输入密码以确认"
            prefix-icon="CircleCheck"
            show-password
          />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model.trim="registerForm.email"
            placeholder="请输入邮箱"
            prefix-icon="Message"
          />
        </el-form-item>

        <el-form-item label="姓名" prop="fullName">
          <el-input
            v-model.trim="registerForm.fullName"
            placeholder="请输入真实姓名"
            prefix-icon="Edit"
          />
        </el-form-item>

        <el-form-item class="submit-item">
          <el-button
            type="primary"
            native-type="submit"
            :loading="loading"
            class="full-width"
          >
            提交注册
          </el-button>
        </el-form-item>

        <div class="login-link">
          <span>
            已有账号？
            <el-link type="primary" :underline="false" @click="router.push('/login')">返回登录</el-link>
          </span>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import { useAuthStore } from "../stores/auth";
import { useUIStore } from "../stores/ui";
import { User, Lock, Message, CircleCheck, Edit, Moon, Sunny } from "@element-plus/icons-vue";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";

const router = useRouter();
const auth = useAuthStore();
const ui = useUIStore();
const { isDark } = storeToRefs(ui);
const registerFormRef = ref<FormInstance>();
const loading = ref(false);

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

const registerForm = reactive({
  username: "",
  password: "",
  confirm: "",
  email: "",
  fullName: "",
});

const validateConfirmPassword = (rule: any, value: any, callback: any) => {
  if (value === "") {
    callback(new Error("请再次输入密码"));
  } else if (value !== registerForm.password) {
    callback(new Error("两次输入的密码不一致"));
  } else {
    callback();
  }
};

const rules = reactive<FormRules>({
  username: [
    { required: true, message: "请输入账号", trigger: "blur" },
    { min: 3, message: "账号长度至少为3位", trigger: "blur" },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 8, message: "密码长度至少为8位", trigger: "blur" },
    {
      pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/,
      message: "密码需包含大小写字母和数字",
      trigger: "blur",
    },
  ],
  confirm: [
    { required: true, validator: validateConfirmPassword, trigger: "blur" },
  ],
  email: [
    { required: true, message: "请输入邮箱", trigger: "blur" },
    { type: "email", message: "请输入有效的邮箱地址", trigger: "blur" },
  ],
  fullName: [{ required: true, message: "请输入姓名", trigger: "blur" }],
});

async function onSubmit() {
  if (!registerFormRef.value) return;

  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        const r = await auth.register(
          registerForm.username,
          registerForm.email,
          registerForm.password,
          registerForm.fullName
        );

        if (r.ok) {
          ElMessage.success("注册成功！");
          router.replace({ name: auth.defaultPage });
        } else {
          ElMessage.error(r.message || "注册失败");
        }
      } catch (err) {
        ElMessage.error("请求出错，请重试");
      } finally {
        loading.value = false;
      }
    }
  });
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
  background-color: var(--app-bg);
  position: relative;
}

.theme-toggle-wrapper {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 10;
}

.register-card {
  width: 100%;
  max-width: 450px;
  border-radius: 12px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--app-border-color);
  background: var(--app-card-bg);
}

:deep(.el-card__body) {
  padding: 24px 40px;
}

.register-header {
  text-align: center;
  margin-bottom: 20px;
}

.register-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--app-text-primary);
  margin: 12px 0 4px;
}

.register-subtitle {
  font-size: 14px;
  color: var(--app-text-secondary);
}

:deep(.el-form-item) {
  margin-bottom: 16px;
}

.form-tip {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
  margin-top: 4px;
  line-height: 1.4;
}

.submit-item {
  margin-top: 24px;
  margin-bottom: 12px !important;
}

.full-width {
  width: 100%;
  height: 40px;
  font-size: 16px;
  font-weight: 600;
}

.login-link {
  text-align: center;
  margin-top: 8px;
  font-size: 14px;
  color: var(--app-text-secondary);
}
</style>
