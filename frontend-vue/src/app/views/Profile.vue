<template>
  <div class="profile-container">
    <div class="page-header">
      <div class="header-content">
        <h2 class="page-title">个人主页</h2>
        <p class="page-subtitle">查看与管理个人基础信息</p>
      </div>
      <el-button disabled>编辑资料</el-button>
    </div>

    <el-card v-loading="loading" shadow="never" class="info-card">
      <template #header>
        <div class="card-header">个人信息</div>
      </template>

      <div v-if="err" class="error-msg">{{ err }}</div>
      <el-row v-else :gutter="20">
        <el-col :span="8">
          <div class="info-item">
            <div class="info-label">用户名</div>
            <div class="info-value">{{ username }}</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <div class="info-label">邮箱</div>
            <div class="info-value">{{ email }}</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <div class="info-label">角色</div>
            <div class="info-value">{{ roleName }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { UserService } from '../api/user.service'
import { RoleLabel } from '../constants/roles'

const auth = useAuthStore()
const { user } = storeToRefs(auth)
const username = ref('')
const email = ref('')
const roleName = ref('')
const loading = ref(true)
const err = ref('')

function normalizeRole(r: string): 'admin' | 'operator' | 'observer' {
  const v = String(r || '').trim().toLowerCase()
  if (v === 'admin' || v === 'administrator') return 'admin'
  if (v === 'operator' || v === 'ops' || v === 'op') return 'operator'
  return 'observer'
}

onMounted(async () => {
  loading.value = true
  err.value = ''
  try {
    const list = await UserService.list()
    const currentName = String(user.value?.username || '')
    const picked = (list || []).find((x: any) => String(x?.username || '') === currentName)
    if (!picked) {
      err.value = '未找到当前用户'
      return
    }
    const name = String(picked?.username || '')
    const emailVal = String(picked?.email || '')
    const roleRaw = String(picked?.role || '')
    const roleKey = normalizeRole(roleRaw)
    username.value = name
    email.value = emailVal
    roleName.value = RoleLabel[roleKey as keyof typeof RoleLabel] || roleRaw || '观察员'
    if (name && name === currentName) {
      auth.user = { username: name, role: roleKey as any }
      auth.persist()
    }
  } catch (e: any) {
    const s = e?.response?.status
    err.value = s === 403 ? '权限不足，无法读取用户列表' : (e.friendlyMessage || '个人信息加载失败')
    ElMessage.error(err.value)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.profile-container {
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
  color: #1f2937;
  margin: 0;
}

.page-subtitle {
  color: #6b7280;
  font-size: 14px;
  margin: 4px 0 0 0;
}

.info-card {
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.card-header {
  font-weight: 600;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  color: #6b7280;
  font-size: 14px;
}

.info-value {
  font-weight: 500;
  color: #1f2937;
}

.error-msg {
  color: #ef4444;
  font-size: 14px;
}
</style>
