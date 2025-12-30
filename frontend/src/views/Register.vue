<template>
  <div class="auth-page">
    <div class="auth-container">
      <!-- Left side - Branding -->
      <div class="auth-branding">
        <div class="branding-content">
          <div class="logo-section">
            <div class="logo">
              <span class="logo-icon">🎙️</span>
            </div>
            <h1 class="brand-name">English <span class="text-gradient">Speaker</span></h1>
          </div>
          
          <h2 class="branding-title">开启你的学习之旅</h2>
          <p class="branding-subtitle">创建账号，立即体验AI驱动的英语口语学习</p>
          
          <div class="branding-features">
            <div class="feature-item">
              <div class="feature-icon">🚀</div>
              <span>快速上手，简单易用</span>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🎓</div>
              <span>个性化学习方案</span>
            </div>
            <div class="feature-item">
              <div class="feature-icon">💪</div>
              <span>持续进步，成就满满</span>
            </div>
          </div>
        </div>
        
        <div class="branding-decoration">
          <div class="decoration-blob blob-1"></div>
          <div class="decoration-blob blob-2"></div>
        </div>
      </div>
      
      <!-- Right side - Register Form -->
      <div class="auth-form-container">
        <div class="auth-form-wrapper">
          <div class="form-header">
            <h2 class="form-title">创建账号</h2>
            <p class="form-subtitle">填写以下信息开始学习</p>
          </div>
          
          <el-form 
            ref="formRef" 
            :model="form" 
            :rules="rules" 
            class="auth-form"
            @submit.prevent="handleRegister"
          >
            <el-form-item prop="username">
              <div class="input-label">
                <span>账号</span>
              </div>
              <el-input
                v-model="form.username"
                placeholder="请输入你的账号"
                size="large"
                clearable
                class="auth-input"
              >
                <template #prefix>
                  <el-icon><User /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item prop="email">
              <div class="input-label">
                <span>邮箱</span>
              </div>
              <el-input
                v-model="form.email"
                type="email"
                placeholder="请输入你的邮箱"
                size="large"
                clearable
                class="auth-input"
              >
                <template #prefix>
                  <el-icon><Message /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item prop="password">
              <div class="input-label">
                <span>密码</span>
              </div>
              <el-input
                v-model="form.password"
                type="password"
                placeholder="至少6位字符"
                size="large"
                show-password
                class="auth-input"
              >
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item prop="confirmPassword">
              <div class="input-label">
                <span>确认密码</span>
              </div>
              <el-input
                v-model="form.confirmPassword"
                type="password"
                placeholder="请再次输入密码"
                size="large"
                show-password
                class="auth-input"
                @keyup.enter="handleRegister"
              >
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              @click="handleRegister"
              class="submit-button"
            >
              <span v-if="!loading">创建账号</span>
              <span v-else>注册中...</span>
            </el-button>
          </el-form>
          
          <div class="form-footer">
            <span class="footer-text">已有账号？</span>
            <button class="link-button" @click="$router.push('/login')">
              立即登录
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { User, Message, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    { min: 3, max: 20, message: '账号长度为3-20个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

async function handleRegister() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.register({
          username: form.username,
          email: form.email,
          password: form.password
        })
        ElMessage.success('注册成功，请登录')
        router.push('/login')
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '注册失败，请重试')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style lang="scss" scoped>
.auth-page {
  min-height: 100vh;
  background: var(--bg-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-lg);
  
  @media (max-width: 968px) {
    padding: 0;
  }
}

.auth-container {
  width: 100%;
  max-width: 1200px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  background: var(--bg-secondary);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-xl);
  overflow: hidden;
  
  @media (max-width: 968px) {
    grid-template-columns: 1fr;
    border-radius: 0;
  }
}

.auth-branding {
  position: relative;
  background: var(--bg-gradient-hero);
  padding: var(--space-3xl);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  
  @media (max-width: 968px) {
    display: none;
  }
}

.branding-content {
  position: relative;
  z-index: 1;
  color: var(--text-inverse);
}

.logo-section {
  margin-bottom: var(--space-2xl);
}

.logo {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-lg);
  
  .logo-icon {
    font-size: 3rem;
  }
}

.brand-name {
  font-family: var(--font-display);
  font-size: 2.5rem;
  font-weight: 800;
  margin: 0;
  
  .text-gradient {
    color: var(--accent);
  }
}

.branding-title {
  font-family: var(--font-display);
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: var(--space-md);
  line-height: 1.3;
}

.branding-subtitle {
  font-size: 1.125rem;
  opacity: 0.9;
  margin-bottom: var(--space-2xl);
  line-height: 1.6;
}

.branding-features {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.feature-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: var(--radius-lg);
  font-weight: 500;
  
  .feature-icon {
    font-size: 1.5rem;
  }
}

.branding-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
  
  .decoration-blob {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);
    filter: blur(40px);
    
    &.blob-1 {
      width: 300px;
      height: 300px;
      top: -100px;
      right: -100px;
    }
    
    &.blob-2 {
      width: 200px;
      height: 200px;
      bottom: -50px;
      left: -50px;
    }
  }
}

.auth-form-container {
  padding: var(--space-3xl);
  display: flex;
  align-items: center;
  justify-content: center;
  
  @media (max-width: 768px) {
    padding: var(--space-2xl) var(--space-lg);
  }
}

.auth-form-wrapper {
  width: 100%;
  max-width: 420px;
}

.form-header {
  margin-bottom: var(--space-2xl);
  text-align: center;
}

.form-title {
  font-family: var(--font-display);
  font-size: 2rem;
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: var(--space-sm);
}

.form-subtitle {
  color: var(--text-secondary);
  font-size: 1rem;
}

.auth-form {
  .el-form-item {
    margin-bottom: var(--space-lg);
  }
}

.input-label {
  margin-bottom: var(--space-sm);
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.auth-input {
  :deep(.el-input__wrapper) {
    padding: var(--space-md) var(--space-lg);
    border-radius: var(--radius-lg);
    box-shadow: none;
    border: 2px solid var(--border-color);
    transition: all var(--transition-base);
    
    &:hover {
      border-color: var(--primary-light);
    }
    
    &.is-focus {
      border-color: var(--primary);
      box-shadow: 0 0 0 4px rgba(255, 107, 53, 0.1);
    }
  }
  
  :deep(.el-input__inner) {
    font-size: 1rem;
    color: var(--text-primary);
    
    &::placeholder {
      color: var(--text-tertiary);
    }
  }
  
  :deep(.el-input__prefix) {
    color: var(--text-tertiary);
    font-size: 1.25rem;
  }
}

.submit-button {
  width: 100%;
  height: 56px;
  margin-top: var(--space-lg);
  font-size: 1.125rem;
  font-weight: 600;
  border-radius: var(--radius-lg);
  background: var(--bg-gradient-primary);
  border: none;
  box-shadow: var(--shadow-colored);
  transition: all var(--transition-base);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-xl);
  }
  
  &:active {
    transform: translateY(0);
  }
}

.form-footer {
  margin-top: var(--space-xl);
  text-align: center;
  color: var(--text-secondary);
  
  .footer-text {
    margin-right: var(--space-sm);
  }
  
  .link-button {
    background: none;
    border: none;
    color: var(--primary);
    font-weight: 600;
    cursor: pointer;
    font-family: var(--font-body);
    font-size: 1rem;
    transition: all var(--transition-fast);
    
    &:hover {
      color: var(--primary-dark);
      text-decoration: underline;
    }
  }
}
</style>
