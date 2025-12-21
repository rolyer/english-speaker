<template>
  <div class="navbar" :class="{ 'mobile': isMobile }">
    <!-- 桌面端顶部导航栏 -->
    <div v-if="!isMobile" class="navbar-desktop">
      <div class="navbar-brand">
        <router-link to="/" class="brand-link">
          <span class="brand-icon">🎓</span>
          <span class="brand-text">英语口语训练</span>
        </router-link>
      </div>
      
      <nav class="navbar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: $route.path === item.path }"
        >
          <el-icon><component :is="icons[item.icon]" /></el-icon>
          <span>{{ item.label }}</span>
        </router-link>
      </nav>
      
      <div class="navbar-actions">
        <template v-if="userStore.isAuthenticated">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" :icon="UserFilled" />
              <span class="username">{{ userStore.user?.username }}</span>
              <el-icon><component :is="ArrowDown" /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="dashboard">
                  <el-icon><component :is="DataAnalysis" /></el-icon>
                  学习进度
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><component :is="SwitchButton" /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <el-button @click="$router.push('/login')" size="small">登录</el-button>
          <el-button type="primary" @click="$router.push('/register')" size="small">注册</el-button>
        </template>
      </div>
    </div>
    
    <!-- 移动端底部导航栏 -->
    <div v-else class="navbar-mobile">
      <router-link
        v-for="item in mobileNavItems"
        :key="item.path"
        :to="item.path"
        class="mobile-nav-item"
        :class="{ active: $route.path === item.path }"
      >
        <el-icon><component :is="icons[item.icon]" /></el-icon>
        <span class="nav-label">{{ item.label }}</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { isMobile } from '@/utils/device'
import {
  HomeFilled,
  ChatDotRound,
  Microphone,
  DataAnalysis,
  UserFilled,
  ArrowDown,
  SwitchButton
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const mobile = computed(() => isMobile())

// 图标映射
const icons = {
  HomeFilled,
  ChatDotRound,
  Microphone,
  DataAnalysis,
  UserFilled,
  ArrowDown,
  SwitchButton
}

const navItems = computed(() => {
  const items = [
    { path: '/', label: '首页', icon: 'HomeFilled' }
  ]
  
  if (userStore.isAuthenticated) {
    items.push(
      { path: '/conversation', label: '文本对话', icon: 'ChatDotRound' },
      { path: '/voice', label: '语音对话', icon: 'Microphone' },
      { path: '/dashboard', label: '学习进度', icon: 'DataAnalysis' }
    )
  }
  
  return items
})

const mobileNavItems = computed(() => {
  const items = [
    { path: '/', label: '首页', icon: 'HomeFilled' }
  ]
  
  if (userStore.isAuthenticated) {
    items.push(
      { path: '/conversation', label: '对话', icon: 'ChatDotRound' },
      { path: '/voice', label: '语音', icon: 'Microphone' },
      { path: '/dashboard', label: '进度', icon: 'DataAnalysis' }
    )
  } else {
    items.push(
      { path: '/login', label: '登录', icon: 'UserFilled' }
    )
  }
  
  return items
})

function handleCommand(command) {
  if (command === 'dashboard') {
    router.push('/dashboard')
  } else if (command === 'logout') {
    userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/')
  }
}
</script>

<style lang="scss" scoped>
.navbar {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  
  &.mobile {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
  }
}

.navbar-desktop {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 64px;
  max-width: 1200px;
  margin: 0 auto;
}

.navbar-brand {
  .brand-link {
    display: flex;
    align-items: center;
    gap: 8px;
    text-decoration: none;
    color: var(--primary-color);
    font-size: 1.2rem;
    font-weight: bold;
    
    .brand-icon {
      font-size: 1.5rem;
    }
    
    &:hover {
      opacity: 0.8;
    }
  }
}

.navbar-nav {
  display: flex;
  gap: 8px;
  flex: 1;
  justify-content: center;
  
  .nav-item {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    border-radius: 8px;
    text-decoration: none;
    color: var(--text-color);
    transition: all 0.3s;
    
    &:hover {
      background: var(--bg-light);
      color: var(--primary-color);
    }
    
    &.active {
      background: var(--primary-color);
      color: white;
    }
  }
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  
  .user-info {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 8px;
    transition: background 0.3s;
    
    &:hover {
      background: var(--bg-light);
    }
    
    .username {
      font-size: 0.9rem;
      color: var(--text-color);
    }
  }
}

.navbar-mobile {
  display: flex;
  justify-content: space-around;
  align-items: center;
  height: 60px;
  padding: 0 8px;
  background: white;
  border-top: 1px solid var(--border-color);
}

.mobile-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding: 8px 4px;
  text-decoration: none;
  color: var(--text-light);
  transition: all 0.3s;
  min-height: 44px; // 触摸友好
  
  .el-icon {
    font-size: 24px;
    margin-bottom: 4px;
  }
  
  .nav-label {
    font-size: 0.75rem;
  }
  
  &:hover,
  &.active {
    color: var(--primary-color);
    
    .el-icon {
      transform: scale(1.1);
    }
  }
  
  &.active {
    .el-icon {
      color: var(--primary-color);
    }
  }
}
</style>

