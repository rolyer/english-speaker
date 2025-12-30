<template>
  <nav class="navbar">
    <div class="navbar-container">
      <!-- Brand Logo -->
      <router-link to="/" class="navbar-brand">
        <div class="brand-icon">🎙️</div>
        <div class="brand-content">
          <span class="brand-name">English Speaker</span>
          <span class="brand-tagline">AI学习助手</span>
        </div>
      </router-link>
      
      <!-- Navigation Links -->
      <div class="nav-links" v-if="userStore.isAuthenticated">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-link"
          :class="{ 'active': isActive(item.path) }"
        >
          <el-icon class="nav-icon">
            <component :is="icons[item.icon]" />
          </el-icon>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </div>
      
      <!-- User Actions -->
      <div class="navbar-actions">
        <template v-if="userStore.isAuthenticated">
          <el-dropdown @command="handleCommand" trigger="click" class="user-dropdown">
            <div class="user-menu">
              <div class="user-avatar">
                <span>{{ getUserInitial }}</span>
              </div>
              <div class="user-info">
                <span class="user-name">{{ userStore.user?.username || '用户' }}</span>
                <span class="user-role">学习者</span>
              </div>
              <el-icon class="dropdown-arrow">
                <ArrowDown />
              </el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="dashboard">
                  <el-icon><DataLine /></el-icon>
                  <span>学习进度</span>
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  <span>退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <el-button 
            class="auth-button login-button" 
            @click="$router.push('/login')"
          >
            登录
          </el-button>
          <el-button 
            type="primary" 
            class="auth-button signup-button" 
            @click="$router.push('/register')"
          >
            注册
          </el-button>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import {
  HomeFilled,
  ChatLineRound,
  Microphone,
  DataLine,
  ArrowDown,
  SwitchButton
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const icons = {
  HomeFilled,
  ChatLineRound,
  Microphone,
  DataLine
}

const navItems = computed(() => [
  { path: '/', label: '首页', icon: 'HomeFilled' },
  { path: '/conversation', label: '文本对话', icon: 'ChatLineRound' },
  { path: '/voice', label: '语音对话', icon: 'Microphone' },
  { path: '/dashboard', label: '学习进度', icon: 'DataLine' }
])

const getUserInitial = computed(() => {
  const username = userStore.user?.username || 'U'
  return username.charAt(0).toUpperCase()
})

function isActive(path) {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}

function handleCommand(command) {
  if (command === 'dashboard') {
    router.push('/dashboard')
  } else if (command === 'logout') {
    userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/')
  }
}

onMounted(async () => {
  if (userStore.isAuthenticated && !userStore.user) {
    try {
      await userStore.fetchUserInfo()
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }
})
</script>

<style lang="scss" scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
  
  @supports (backdrop-filter: blur(10px)) {
    background: rgba(255, 255, 255, 0.8);
  }
}

.navbar-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 var(--space-xl);
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-xl);
  
  @media (max-width: 768px) {
    padding: 0 var(--space-lg);
    height: 64px;
    gap: var(--space-md);
  }
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  text-decoration: none;
  transition: transform var(--transition-base);
  
  &:hover {
    transform: translateY(-1px);
  }
}

.brand-icon {
  width: 48px;
  height: 48px;
  background: var(--bg-gradient-primary);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
  box-shadow: var(--shadow-md);
  
  @media (max-width: 768px) {
    width: 40px;
    height: 40px;
    font-size: 1.5rem;
  }
}

.brand-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
  
  @media (max-width: 560px) {
    display: none;
  }
}

.brand-name {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

.brand-tagline {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  font-weight: 500;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  flex: 1;
  justify-content: center;
  
  @media (max-width: 860px) {
    display: none;
  }
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-lg);
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 0.9375rem;
  transition: all var(--transition-base);
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%) scaleX(0);
    width: 80%;
    height: 2px;
    background: var(--bg-gradient-primary);
    border-radius: 2px;
    transition: transform var(--transition-base);
  }
  
  &:hover {
    color: var(--primary);
    background: rgba(255, 107, 53, 0.05);
  }
  
  &.active {
    color: var(--primary);
    font-weight: 600;
    
    &::after {
      transform: translateX(-50%) scaleX(1);
    }
  }
}

.nav-icon {
  font-size: 1.25rem;
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.auth-button {
  height: 42px;
  padding: 0 var(--space-xl);
  border-radius: var(--radius-lg);
  font-weight: 600;
  font-size: 0.9375rem;
  transition: all var(--transition-base);
  
  @media (max-width: 560px) {
    padding: 0 var(--space-lg);
    font-size: 0.875rem;
  }
}

.login-button {
  border: 2px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  
  &:hover {
    border-color: var(--primary);
    color: var(--primary);
    background: rgba(255, 107, 53, 0.05);
  }
}

.signup-button {
  background: var(--bg-gradient-primary);
  border: none;
  box-shadow: var(--shadow-md);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
  }
}

.user-dropdown {
  cursor: pointer;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
  border: 2px solid transparent;
  
  &:hover {
    background: var(--bg-tertiary);
    border-color: var(--border-color);
  }
  
  @media (max-width: 560px) {
    padding: var(--space-sm);
  }
}

.user-avatar {
  width: 42px;
  height: 42px;
  border-radius: var(--radius-lg);
  background: var(--bg-gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-inverse);
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 1.125rem;
  box-shadow: var(--shadow-sm);
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  
  @media (max-width: 560px) {
    display: none;
  }
}

.user-name {
  font-weight: 600;
  font-size: 0.9375rem;
  color: var(--text-primary);
  line-height: 1;
}

.user-role {
  font-size: 0.75rem;
  color: var(--text-tertiary);
}

.dropdown-arrow {
  font-size: 1rem;
  color: var(--text-tertiary);
  transition: transform var(--transition-base);
  
  @media (max-width: 560px) {
    display: none;
  }
}

.user-menu:hover .dropdown-arrow {
  transform: translateY(2px);
}

:deep(.el-dropdown-menu) {
  margin-top: var(--space-md);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-lg);
  padding: var(--space-sm);
  min-width: 180px;
}

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  border-radius: var(--radius-md);
  font-weight: 500;
  font-size: 0.9375rem;
  transition: all var(--transition-fast);
  
  .el-icon {
    font-size: 1.125rem;
  }
  
  &:hover {
    background: var(--bg-tertiary);
    color: var(--primary);
  }
  
  &.is-divided {
    margin-top: var(--space-xs);
    padding-top: var(--space-md);
    border-top: 1px solid var(--border-color);
    
    &:hover {
      color: var(--error);
    }
  }
}
</style>
