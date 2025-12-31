<template>
  <div class="profile-page">
    <!-- Header -->
    <div class="profile-header">
      <div class="header-content">
        <h1 class="page-title">
          <span class="title-icon">👤</span>
          <span>个人资料</span>
        </h1>
      </div>
    </div>

    <!-- Content -->
    <div class="profile-content">
      <div class="profile-container">
        <!-- 基本信息卡片 -->
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">基本信息</span>
            </div>
          </template>

          <el-form
            ref="profileFormRef"
            :model="profileForm"
            :rules="profileRules"
            label-width="100px"
            label-position="left"
          >
            <el-form-item label="用户名">
              <el-input v-model="userStore.user.username" disabled />
            </el-form-item>

            <el-form-item label="邮箱">
              <el-input v-model="userStore.user.email" disabled />
            </el-form-item>

            <el-form-item label="昵称" prop="nickname">
              <el-input
                v-model="profileForm.nickname"
                placeholder="请输入昵称"
                maxlength="50"
                show-word-limit
              />
            </el-form-item>

            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="profileForm.gender">
                <el-radio label="male">男</el-radio>
                <el-radio label="female">女</el-radio>
                <el-radio label="other">其他</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="年龄" prop="age">
              <el-input-number
                v-model="profileForm.age"
                :min="1"
                :max="150"
                placeholder="请输入年龄"
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                :loading="updating"
                @click="handleUpdateProfile"
              >
                保存修改
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 修改密码卡片 -->
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">修改密码</span>
            </div>
          </template>

          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-width="100px"
            label-position="left"
          >
            <el-form-item label="旧密码" prop="oldPassword">
              <el-input
                v-model="passwordForm.oldPassword"
                type="password"
                placeholder="请输入旧密码"
                show-password
              />
            </el-form-item>

            <el-form-item label="新密码" prop="newPassword">
              <el-input
                v-model="passwordForm.newPassword"
                type="password"
                placeholder="请输入新密码（至少6位）"
                show-password
              />
            </el-form-item>

            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input
                v-model="passwordForm.confirmPassword"
                type="password"
                placeholder="请再次输入新密码"
                show-password
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                :loading="changingPassword"
                @click="handleChangePassword"
              >
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 账号信息卡片 -->
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">账号信息</span>
            </div>
          </template>

          <div class="account-info">
            <div class="info-item">
              <span class="info-label">注册时间：</span>
              <span class="info-value">{{ formatDate(userStore.user.created_at) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">账号状态：</span>
              <span class="info-value status-active">正常</span>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import api from '@/services/api'

const userStore = useUserStore()

const profileFormRef = ref(null)
const passwordFormRef = ref(null)
const updating = ref(false)
const changingPassword = ref(false)

// 个人资料表单
const profileForm = reactive({
  nickname: '',
  gender: '',
  age: null
})

// 密码表单
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 表单验证规则
const profileRules = {
  nickname: [
    { max: 50, message: '昵称长度不能超过50个字符', trigger: 'blur' }
  ],
  age: [
    { type: 'number', min: 1, max: 150, message: '年龄必须在1-150之间', trigger: 'blur' }
  ]
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入旧密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 加载用户资料
async function loadProfile() {
  try {
    const response = await api.get('/profile')
    profileForm.nickname = response.nickname || ''
    profileForm.gender = response.gender || ''
    profileForm.age = response.age || null
    
    // 更新 store 中的用户信息
    userStore.user = {
      ...userStore.user,
      nickname: response.nickname,
      gender: response.gender,
      age: response.age,
      created_at: response.created_at
    }
  } catch (error) {
    console.error('加载用户资料失败:', error)
    ElMessage.error('加载用户资料失败')
  }
}

// 更新个人资料
async function handleUpdateProfile() {
  if (!profileFormRef.value) return
  
  await profileFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    updating.value = true
    try {
      const response = await api.put('/profile', {
        nickname: profileForm.nickname || null,
        gender: profileForm.gender || null,
        age: profileForm.age || null
      })
      
      // 更新 store
      userStore.user = {
        ...userStore.user,
        nickname: response.nickname,
        gender: response.gender,
        age: response.age
      }
      
      ElMessage.success('个人资料更新成功')
    } catch (error) {
      console.error('更新个人资料失败:', error)
      ElMessage.error(error.response?.data?.detail || '更新个人资料失败')
    } finally {
      updating.value = false
    }
  })
}

// 修改密码
async function handleChangePassword() {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    changingPassword.value = true
    try {
      await api.post('/profile/change-password', {
        old_password: passwordForm.oldPassword,
        new_password: passwordForm.newPassword
      })
      
      ElMessage.success('密码修改成功，请重新登录')
      
      // 清空表单
      passwordForm.oldPassword = ''
      passwordForm.newPassword = ''
      passwordForm.confirmPassword = ''
      passwordFormRef.value.resetFields()
      
      // 延迟后退出登录
      setTimeout(() => {
        userStore.logout()
      }, 1500)
    } catch (error) {
      console.error('修改密码失败:', error)
      ElMessage.error(error.response?.data?.detail || '修改密码失败')
    } finally {
      changingPassword.value = false
    }
  })
}

// 格式化日期
function formatDate(dateString) {
  if (!dateString) return '未知'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

onMounted(() => {
  loadProfile()
})
</script>

<style lang="scss" scoped>
.profile-page {
  min-height: calc(100vh - 72px);
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  
  @media (max-width: 768px) {
    min-height: calc(100vh - 64px);
  }
  
  @media (max-width: 860px) {
    min-height: calc(100vh - 64px - 72px);
  }
}

.profile-header {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  padding: var(--space-lg) var(--space-xl);
  
  @media (max-width: 768px) {
    padding: var(--space-md) var(--space-lg);
  }
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin: 0;
  
  .title-icon {
    font-size: 1.75rem;
  }
  
  @media (max-width: 768px) {
    font-size: 1.25rem;
    
    .title-icon {
      font-size: 1.5rem;
    }
  }
}

.profile-content {
  flex: 1;
  padding: var(--space-2xl) var(--space-xl);
  overflow-y: auto;
  
  @media (max-width: 768px) {
    padding: var(--space-xl) var(--space-lg);
  }
}

.profile-container {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

.info-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  
  :deep(.el-card__header) {
    padding: var(--space-lg) var(--space-xl);
    border-bottom: 1px solid var(--border-color);
  }
  
  :deep(.el-card__body) {
    padding: var(--space-xl);
  }
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.account-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.info-item {
  display: flex;
  align-items: center;
  padding: var(--space-sm) 0;
}

.info-label {
  font-weight: 500;
  color: var(--text-secondary);
  min-width: 100px;
}

.info-value {
  color: var(--text-primary);
  
  &.status-active {
    color: var(--success);
    font-weight: 500;
  }
}

:deep(.el-form-item) {
  margin-bottom: var(--space-lg);
}

:deep(.el-input),
:deep(.el-input-number) {
  width: 100%;
}

:deep(.el-button) {
  min-width: 120px;
}
</style>

