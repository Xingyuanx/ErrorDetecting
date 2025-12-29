<template>
  <section class="container">
    <!-- 样式复用自 Login.vue -->
    <form class="form" @submit.prevent="onSubmit">
      <div style="text-align: center; width: 100%">
        <h1
          style="
            font-size: 1.5rem;
            color: var(--bg-dark);
            margin-bottom: 0.5rem;
          "
        >
          新用户注册
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

      <span class="input-span">
        <label for="confirm" class="label">确认密码</label>
        <div class="password-group">
          <input
            :type="showConfirm ? 'text' : 'password'"
            name="confirm"
            id="confirm"
            v-model.trim="confirm"
          />
          <i
            class="fas"
            :class="showConfirm ? 'fa-eye' : 'fa-eye-slash'"
            @click="showConfirm = !showConfirm"
          ></i>
        </div>
      </span>

      <span class="input-span">
        <label for="email" class="label">邮箱</label>
        <input type="email" name="email" id="email" v-model.trim="email" />
      </span>

      <span class="input-span">
        <label for="fullName" class="label">姓名</label>
        <input
          type="text"
          name="fullName"
          id="fullName"
          v-model.trim="fullName"
        />
      </span>

      <button class="submit-btn" type="submit" :disabled="loading">
        {{ loading ? "提交中..." : "提交" }}
      </button>
      <span class="span"
        >已有账号？ <RouterLink to="/login">返回登录</RouterLink></span
      >

      <div
        v-if="msg"
        class="register__msg"
        style="text-align: center; color: #f43f5e; font-size: 0.9rem"
      >
        {{ msg }}
      </div>
    </form>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
const username = ref("");
const password = ref("");
const confirm = ref("");
const email = ref("");
const fullName = ref("");
const showPassword = ref(false);
const showConfirm = ref(false);
// const role = ref('operator') // 未使用
const msg = ref("");
const loading = ref(false);
const router = useRouter();
const auth = useAuthStore();
async function onSubmit() {
  loading.value = true;
  if (
    !username.value ||
    !password.value ||
    !confirm.value ||
    !email.value ||
    !fullName.value
  ) {
    msg.value = "请填写所有必填字段";
    loading.value = false;
    return;
  }
  if (password.value !== confirm.value) {
    msg.value = "两次密码不一致";
    loading.value = false;
    return;
  }
  const r = await auth.register(
    username.value,
    email.value,
    password.value,
    fullName.value
  );
  if (r.ok) router.replace({ name: auth.defaultPage });
  else msg.value = r.message || "注册失败";
  loading.value = false;
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
  gap: 0.6rem; /* 减小行间距 */
  width: 100%;
  max-width: 400px;
  background: white; /* 改为不透明白色 */
  padding: 1.5rem; /* 减小容器内边距 */
  border-radius: 20px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
}

.form .input-span {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0.2rem; /* 减小 label 和 input 的间距 */
}

.password-group {
  position: relative;
  width: 100%;
  display: flex;
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

.form input[type="text"],
.form input[type="password"],
.form input[type="email"] {
  border-radius: 0.5rem;
  padding: 0.6rem 0.75rem; /* 减小输入框高度 */
  width: 100%;
  border: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: var(--clr-alpha);
  outline: 2px solid var(--bg-dark);
}

.form input[name="password"],
.form input[name="confirm"] {
  padding-right: 2.5rem;
}

.form input[type="text"]:focus,
.form input[type="password"]:focus,
.form input[type="email"]:focus {
  outline: 2px solid var(--clr);
}

.label {
  align-self: flex-start;
  color: var(--clr);
  font-weight: 600;
}

/* From Uiverse.io by biswacpcode */
.submit-btn {
  color: var(--bg-light);
  text-decoration: none;
  font-size: 25px;
  border: none;
  background-color: var(--bg-dark);
  padding: 0.5rem 1rem;
  border-radius: 3rem;
  font-weight: 600;
  font-family: "Poppins", sans-serif;
  cursor: pointer;
  width: 100%;
  position: relative;
  overflow: hidden;
  margin-top: 1rem;
}

.submit-btn::before {
  margin-left: auto;
}

.submit-btn::after,
.submit-btn::before {
  content: "";
  width: 0%;
  height: 2px;
  background: var(--clr);
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
</style>
