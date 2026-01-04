<template>
  <div class="account-container">
    <div class="page-header">
      <div class="header-content">
        <h2 class="page-title">账号管理</h2>
        <p class="page-subtitle">修改密码、设置双因素认证等</p>
      </div>
      <el-button type="primary" :loading="loading" @click="save">保存设置</el-button>
    </div>

    <el-card shadow="never" class="settings-card">
      <template #header>
        <div class="card-header">安全设置</div>
      </template>
      <el-form label-position="top" :model="form" @submit.prevent="save">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="当前密码">
              <el-input v-model.trim="form.current" type="password" show-password placeholder="••••••••" autocomplete="current-password" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="新密码">
              <el-input v-model.trim="form.next" type="password" show-password placeholder="至少8位" autocomplete="new-password" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="确认新密码">
              <el-input v-model.trim="form.confirm" type="password" show-password placeholder="再次输入" autocomplete="new-password" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { UserService } from '../api/user.service'

const form = reactive({ current: '', next: '', confirm: '' })
const loading = ref(false)

async function save() {
  if (!form.current || !form.next || !form.confirm) {
    ElMessage.warning('请填写完整密码信息')
    return
  }
  if (form.next.length < 8) {
    ElMessage.warning('新密码至少8位')
    return
  }
  if (form.next !== form.confirm) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }

  loading.value = true
  try {
    const r = await UserService.updatePassword({
      currentPassword: form.current,
      newPassword: form.next
    })

    if (r?.ok || r?.data?.ok || r?.status === 'success') {
      ElMessage.success('密码修改成功')
      form.current = ''
      form.next = ''
      form.confirm = ''
    } else {
      ElMessage.error(r?.detail || r?.message || '修改失败')
    }
  } catch (e: any) {
    const detail = e.friendlyMessage || e.response?.data?.detail
    let msg = e.friendlyMessage || '服务器错误，请稍后再试'
    if (detail === 'invalid_current_password') msg = '当前密码错误'
    else if (detail === 'weak_new_password') msg = '新密码太弱（需包含大小写字母和数字）'
    else if (detail === 'demo_user_cannot_change_password') msg = '演示账号不允许修改密码'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.account-container {
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

.settings-card {
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.card-header {
  font-weight: 600;
}
</style>
