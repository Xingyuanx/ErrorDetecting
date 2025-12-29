<template>
  <section class="container">
    <!-- From Uiverse.io by bociKond -->
    <form class="form" @submit.prevent="onSubmit">
      <div style="text-align: center; width: 100%">
        <h1
          style="
            font-size: 1.5rem;
            color: var(--bg-dark);
            margin-bottom: 0.5rem;
          "
        >
          集群管理系统
        </h1>
      </div>

      <span class="input-span">
        <label for="username" class="label">账号</label>
        <input
          type="text"
          name="username"
          id="username"
          v-model.trim="username"
        />
      </span>
      <span class="input-span">
        <label for="password" class="label">密码</label>
        <div class="password-group">
          <input
            :type="showPassword ? 'text' : 'password'"
            name="password"
            id="password"
            v-model.trim="password"
          />
          <i
            class="fas"
            :class="showPassword ? 'fa-eye' : 'fa-eye-slash'"
            @click="showPassword = !showPassword"
          ></i>
        </div>
      </span>
      <span class="span"><a href="#">忘记密码?</a></span>
      <button class="submit-btn" type="submit" :disabled="loading">
        {{ loading ? "登录中..." : "登录" }}
      </button>
      <span class="span"
        >还没有账号？ <RouterLink to="/register">立即注册</RouterLink></span
      >

      <!-- 保留原有提示信息 -->
      <div v-if="msg" style="color: #f43f5e; font-size: 0.9rem">{{ msg }}</div>
      <div
        style="
          font-size: 0.8rem;
          color: var(--bg-dark);
          opacity: 0.8;
          text-align: center;
        "
      >
        演示账户：账号 123 ，密码 123
      </div>
      <div
        class="login__health"
        :data-status="health"
        style="font-size: 0.75rem"
      >
        后端连接：{{
          health === "ok" ? "正常" : health === "fail" ? "异常" : "检测中"
        }}
      </div>
    </form>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import api from "../lib/api";
const username = ref("");
const password = ref("");
const showPassword = ref(false);
const msg = ref("");
const loading = ref(false);
const health = ref<"ok" | "fail" | "checking">("checking");
const router = useRouter();
const auth = useAuthStore();
onMounted(async () => {
  try {
    await api.get("/v1/health");
    health.value = "ok";
  } catch {
    health.value = "fail";
  }
});
async function onSubmit() {
  loading.value = true;
  const r = await auth.login(username.value, password.value);
  loading.value = false;
  if (r.ok) router.replace({ name: auth.defaultPage });
  else msg.value = r.message || "登录失败！";
}
</script>

<style scoped>
/* From Uiverse.io by csemszepp */
.container {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1; /* 让 container 撑满父容器 flex 空间 */
  width: 100%;
  min-width: 100%;
  min-height: calc(100vh - var(--header-h));
  --s: 200px; /* control the size */
  --c1: #1d1d1d;
  --c2: #4e4f51;
  --c3: #3c3c3c;

  background: repeating-conic-gradient(
        from 30deg,
        #0000 0 120deg,
        var(--c3) 0 180deg
      )
      calc(0.5 * var(--s)) calc(0.5 * var(--s) * 0.577),
    repeating-conic-gradient(
      from 30deg,
      var(--c1) 0 60deg,
      var(--c2) 0 120deg,
      var(--c3) 0 180deg
    );
  background-size: var(--s) calc(var(--s) * 0.577);
}

/* From Uiverse.io by bociKond */
.form {
  --bg-light: #efefef;
  --bg-dark: #707070;
  --clr: #58bc82;
  --clr-alpha: #9c9c9c60;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  width: 100%;
  max-width: 400px;
  background: white; /* 改为不透明白色 */
  padding: 2rem;
  border-radius: 20px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
}

.form .input-span {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.password-group {
  position: relative;
  width: 100%;
  display: flex; /* 确保 input 撑满 */
}

.password-group i {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: var(--bg-dark);
  opacity: 0.7;
  font-size: 1rem;
  z-index: 10;
}

.password-group i:hover {
  opacity: 1;
  color: var(--clr);
}

.form input[type="text"], /* 原CSS是 type="email"，这里适配 text */
.form input[type="password"] {
  border-radius: 0.5rem;
  padding: 1rem 0.75rem;
  width: 100%;
  border: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: var(--clr-alpha);
  outline: 2px solid var(--bg-dark);
}

.form input[name="password"] {
  padding-right: 2.5rem;
}

.form input[type="text"]:focus,
.form input[type="password"]:focus {
  outline: 2px solid var(--clr);
}

.label {
  align-self: flex-start;
  color: var(--clr);
  font-weight: 600;
}

/* From Uiverse.io by biswacpcode */
.submit-btn {
  color: var(--bg-light); /* 恢复白色文字 */
  text-decoration: none;
  font-size: 25px;
  border: none;
  background-color: var(--bg-dark); /* 恢复灰色背景 */
  padding: 0.5rem 1rem; /* 添加适当的内边距 */
  border-radius: 3rem; /* 恢复圆角 */
  font-weight: 600;
  font-family: "Poppins", sans-serif;
  cursor: pointer;
  width: 100%;
  position: relative; /* 确保伪元素定位正确 */
  overflow: hidden; /* 防止伪元素溢出圆角（可选，看效果）- 这里先不加，因为下划线可能需要在边缘 */
}

.submit-btn::before {
  margin-left: auto;
}

.submit-btn::after,
.submit-btn::before {
  content: "";
  width: 0%;
  height: 2px;
  background: var(--clr); /* 原为 #f44336，改为 var(--clr) 与 label 保持一致 */
  display: block;
  transition: 0.5s;
}

.submit-btn:hover::after,
.submit-btn:hover::before {
  width: 100%;
}

.span {
  text-decoration: none;
  color: var(--bg-dark);
  font-size: 0.9rem;
}

.span a {
  color: var(--clr);
  text-decoration: none;
}

/* 状态颜色 */
.login__health[data-status="ok"] {
  color: #10b981;
}
.login__health[data-status="fail"] {
  color: #f43f5e;
}
</style>
