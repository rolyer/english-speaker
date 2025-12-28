<template>
  <div class="navbar" :class="{ 'mobile': mobile }">
    <!-- 桌面端顶部导航栏 -->
    <div v-if="!mobile" class="navbar-desktop">
      <div class="navbar-brand">
        <router-link to="/" class="brand-link">
          <span class="brand-icon">🎓</span>
          <span class="brand-text">英语口语训练</span>
        </router-link>
      </div>
      
      <nav v-if="userStore.isAuthenticated" class="navbar-nav">
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
          <el-dropdown @command="handleCommand" trigger="click">
            <div class="user-info">
              <el-avatar :size="36" class="user-avatar">
                <el-icon><UserFilled /></el-icon>
              </el-avatar>
              <span v-if="userStore.user" class="username">{{ userStore.user.username }}</span>
              <span v-else class="username">加载中...</span>
              <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="dashboard">
                  <el-icon><DataAnalysis /></el-icon>
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
          <el-button @click="$router.push('/login')" size="default">登录</el-button>
          <el-button type="primary" @click="$router.push('/register')" size="default">注册</el-button>
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
import { computed, onMounted, watch } from 'vue'
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

// 监听用户信息变化
watch(() => userStore.user, (newUser) => {
  console.log('[NavBar] 用户信息变化:', newUser)
}, { deep: true })

// 确保用户信息已加载
onMounted(async () => {
  console.log('[NavBar] onMounted - 检查用户状态:', {
    isAuthenticated: userStore.isAuthenticated,
    hasUser: !!userStore.user,
    user: userStore.user
  })
  
  if (userStore.isAuthenticated && !userStore.user) {
    console.log('[NavBar] 正在获取用户信息...')
    try {
      await userStore.fetchUserInfo()
      console.log('[NavBar] 用户信息获取成功:', userStore.user)
    } catch (error) {
      console.error('[NavBar] 获取用户信息失败:', error)
    }
  }
})

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
    gap: 10px;
    cursor: pointer;
    padding: 6px 12px;
    border-radius: 20px;
    transition: all 0.3s ease;
    border: 1px solid transparent;
    
    &:hover {
      background: var(--bg-light);
      border-color: var(--border-color);
    }
    
    .user-avatar {
      background: linear-gradient(135deg, var(--primary-color), #667eea);
      color: white;
      flex-shrink: 0;
    }
    
    .username {
      font-size: 0.95rem;
      font-weight: 500;
      color: var(--text-color);
      max-width: 120px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    
    .dropdown-icon {
      font-size: 14px;
      color: var(--text-light);
      transition: transform 0.3s ease;
    }
    
    &:hover .dropdown-icon {
      transform: translateY(2px);
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

// 下拉菜单样式优化
:deep(.el-dropdown-menu) {
  padding: 8px 0;
  min-width: 160px;
  
  .el-dropdown-menu__item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 16px;
    font-size: 0.9rem;
    
    .el-icon {
      font-size: 16px;
    }
    
    &:hover {
      background: var(--bg-light);
      color: var(--primary-color);
    }
  }
  
  .el-dropdown-menu__item--divided {
    border-top: 1px solid var(--border-color);
    margin-top: 4px;
    
    &:hover {
      color: var(--el-color-danger);
    }
  }
}
</style>

