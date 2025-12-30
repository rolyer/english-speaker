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
          
          <h2 class="branding-title">AI驱动的英语口语学习</h2>
          <p class="branding-subtitle">与智能AI对话，快速提升英语口语能力</p>
          
          <div class="branding-features">
            <div class="feature-item">
              <div class="feature-icon">✨</div>
              <span>智能AI对话</span>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🎯</div>
              <span>实时发音评分</span>
            </div>
            <div class="feature-item">
              <div class="feature-icon">📊</div>
              <span>学习进度追踪</span>
            </div>
          </div>
        </div>
        
        <div class="branding-decoration">
          <div class="decoration-blob blob-1"></div>
          <div class="decoration-blob blob-2"></div>
        </div>
      </div>
      
      <!-- Right side - Login Form -->
      <div class="auth-form-container">
        <div class="auth-form-wrapper">
          <div class="form-header">
            <h2 class="form-title">欢迎回来</h2>
            <p class="form-subtitle">登录你的账号继续学习</p>
          </div>
          
          <el-form 
            ref="formRef" 
            :model="form" 
            :rules="rules" 
            class="auth-form"
            @submit.prevent="handleLogin"
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
            
            <el-form-item prop="password">
              <div class="input-label">
                <span>密码</span>
              </div>
              <el-input
                v-model="form.password"
                type="password"
                placeholder="请输入你的密码"
                size="large"
                show-password
                class="auth-input"
                @keyup.enter="handleLogin"
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
              @click="handleLogin"
              class="submit-button"
            >
              <span v-if="!loading">登录</span>
              <span v-else>登录中...</span>
            </el-button>
          </el-form>
          
          <div class="form-footer">
            <span class="footer-text">还没有账号？</span>
            <button class="link-button" @click="$router.push('/register')">
              立即注册
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入账号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

async function handleLogin() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.login(form.username, form.password)
        ElMessage.success('登录成功')
        const redirect = route.query.redirect || '/voice'
        router.push(redirect)
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '登录失败，请检查账号和密码')
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
    margin-bottom: var(--space-xl);
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
