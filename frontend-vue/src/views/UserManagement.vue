<template>
  <div class="user-management-container">
    <div class="page-header">
      <h2 class="page-title">用户管理</h2>
      <el-button type="primary" @click="open = true">新增用户</el-button>
    </div>

    <el-card class="table-card" shadow="never">
      <el-table
        :data="displayUsers"
        stripe
        style="width: 100%"
        header-cell-class-name="table-header"
      >
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column label="角色" width="150">
          <template #default="{ row }">
            <el-select
              v-model="row.role"
              size="small"
              :disabled="changingRoleUser === row.username"
              @change="(val: string) => onRoleChange(row.username, val)"
            >
              <el-option label="管理员" value="admin" />
              <el-option label="操作员" value="operator" />
              <el-option label="观察员" value="observer" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">
              {{ statusName(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              type="warning"
              plain
              v-if="row.status !== 'disabled'"
              @click="ban(row.username)"
              >封禁</el-button
            >
            <el-button
              size="small"
              type="success"
              plain
              v-else
              @click="unban(row.username)"
              >解禁</el-button
            >
            <el-popconfirm
              title="确认删除此用户？"
              @confirm="del(row.username)"
            >
              <template #reference>
                <el-button size="small" type="danger" plain>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :layout="
            isMobile
              ? 'prev, pager, next'
              : 'total, sizes, prev, pager, next, jumper'
          "
          :pager-count="isMobile ? 5 : 7"
          :small="isMobile"
          :total="users.length"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="open"
      title="新增系统用户"
      :width="isMobile ? '95%' : '600px'"
      @closed="cancel"
    >
      <el-form :model="form" label-width="100px" label-position="right">
        <el-form-item label="用户名" required>
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="姓名" required>
          <el-input v-model="form.fullName" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="邮箱" required>
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="密码" required>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" required>
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="请再次确认密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="角色" required>
          <el-select v-model="form.role" class="w-full">
            <el-option label="管理员" value="admin" />
            <el-option label="操作员" value="operator" />
            <el-option label="观察员" value="observer" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" required>
          <el-select v-model="form.status" class="w-full">
            <el-option label="启用" value="enabled" />
            <el-option label="待审核" value="pending" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="open = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="save"
            >保存用户</el-button
          >
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, onMounted, onUnmounted } from "vue";
import { useAuthStore } from "../stores/auth";
import { UserService } from "../api/user.service";
import { ElMessage } from "element-plus";

const auth = useAuthStore();
const isMobile = ref(window.innerWidth < 768);
const updateWidth = () => {
  isMobile.value = window.innerWidth < 768;
};

const users = reactive<
  { username: string; email: string; role: string; status: string }[]
>([]);
const open = ref(false);
const saving = ref(false);
const changingRoleUser = ref("");
const form = reactive({
  username: "",
  fullName: "",
  email: "",
  password: "",
  confirmPassword: "",
  role: "operator",
  status: "enabled",
});

// 分页相关状态
const currentPage = ref(1);
const pageSize = ref(10);

// 计算当前页显示的用户
const displayUsers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return users.slice(start, end);
});

function handleSizeChange(val: number) {
  pageSize.value = val;
  currentPage.value = 1;
}

function handleCurrentChange(val: number) {
  currentPage.value = val;
}

function statusName(s: string) {
  if (s === "enabled") return "启用";
  if (s === "pending") return "待审核";
  if (s === "disabled") return "禁用";
  return s;
}

function statusType(s: string) {
  if (s === "enabled") return "success";
  if (s === "pending") return "warning";
  if (s === "disabled") return "danger";
  return "info";
}

async function load() {
  try {
    const data = await UserService.list();
    const list = Array.isArray(data)
      ? data.map((u: any) => ({
          username: u.username || u.user_name || u.name,
          email: u.email || u.mail,
          role: u.role,
          status: u.status,
        }))
      : [];
    users.splice(0, users.length, ...list);
  } catch (e: any) {
    ElMessage.error(e.friendlyMessage || "加载失败");
  }
}

async function save() {
  if (
    !form.username ||
    !form.fullName ||
    !form.email ||
    !form.role ||
    !form.status
  ) {
    ElMessage.warning("请填写完整信息");
    return;
  }
  if (!form.password || !form.confirmPassword) {
    ElMessage.warning("请输入密码并确认");
    return;
  }
  if (form.password !== form.confirmPassword) {
    ElMessage.warning("两次密码不一致");
    return;
  }

  try {
    saving.value = true;
    const payload = {
      username: form.username,
      full_name: form.fullName,
      email: form.email,
      role: form.role,
      status: form.status,
      password: form.password,
    };
    await UserService.create(payload);
    ElMessage.success("保存成功");
    await load();
    open.value = false;
  } catch (e: any) {
    ElMessage.error(e.friendlyMessage || "保存失败");
  } finally {
    saving.value = false;
  }
}

function cancel() {
  open.value = false;
  Object.assign(form, {
    username: "",
    fullName: "",
    email: "",
    password: "",
    confirmPassword: "",
    role: "operator",
    status: "enabled",
  });
}

async function ban(u: string) {
  try {
    await UserService.update(u, { status: "disabled" });
    ElMessage.success("已封禁");
    await load();
  } catch (e: any) {
    ElMessage.error(e.friendlyMessage || "操作失败");
  }
}

async function unban(u: string) {
  try {
    await UserService.update(u, { status: "enabled" });
    ElMessage.success("已解禁");
    await load();
  } catch (e: any) {
    ElMessage.error(e.friendlyMessage || "操作失败");
  }
}

async function del(u: string) {
  try {
    await UserService.remove(u);
    ElMessage.success("已删除");
    await load();
  } catch (e: any) {
    ElMessage.error(e.friendlyMessage || "删除失败");
  }
}

async function onRoleChange(u: string, r: string) {
  try {
    changingRoleUser.value = u;
    await UserService.update(u, { role: r });
    ElMessage.success("角色已更新");
    await load();
  } catch (e: any) {
    ElMessage.error(e.friendlyMessage || "修改角色失败");
  } finally {
    changingRoleUser.value = "";
  }
}

onMounted(() => {
  load();
  window.addEventListener("resize", updateWidth);
});

onUnmounted(() => {
  window.removeEventListener("resize", updateWidth);
});
</script>

<style scoped>
.user-management-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--app-text-primary);
  margin: 0;
}

.table-card {
  border-radius: 8px;
  border: 1px solid var(--app-border-color);
  background: var(--app-card-bg);
}

.w-full {
  width: 100%;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .pagination-wrapper {
    justify-content: center;
  }
}
</style>
