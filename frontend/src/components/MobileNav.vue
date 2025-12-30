<template>
  <nav class="mobile-nav">
    <router-link
      v-for="item in navItems"
      :key="item.path"
      :to="item.path"
      class="nav-item"
      :class="{ 'active': isActive(item.path) }"
    >
      <el-icon class="nav-icon">
        <component :is="icons[item.icon]" />
      </el-icon>
      <span class="nav-label">{{ item.label }}</span>
    </router-link>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import {
  HomeFilled,
  ChatLineRound,
  Microphone,
  DataLine
} from '@element-plus/icons-vue'

const route = useRoute()
const userStore = useUserStore()

const icons = {
  HomeFilled,
  ChatLineRound,
  Microphone,
  DataLine
}

const navItems = computed(() => {
  const items = [
    { path: '/', label: '首页', icon: 'HomeFilled' }
  ]
  
  if (userStore.isAuthenticated) {
    items.push(
      { path: '/conversation', label: '文本', icon: 'ChatLineRound' },
      { path: '/voice', label: '语音', icon: 'Microphone' },
      { path: '/dashboard', label: '进度', icon: 'DataLine' }
    )
  }
  
  return items
})

function isActive(path) {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}
</script>

<style lang="scss" scoped>
.mobile-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  display: none;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
  padding: var(--space-xs) var(--space-md) calc(var(--space-xs) + env(safe-area-inset-bottom));
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  
  @supports (backdrop-filter: blur(10px)) {
    background: rgba(255, 255, 255, 0.9);
  }
  
  @media (max-width: 860px) {
    display: flex;
    align-items: center;
    justify-content: space-around;
    gap: var(--space-xs);
  }
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: var(--text-tertiary);
  transition: all var(--transition-base);
  min-width: 64px;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%) scaleX(0);
    width: 40px;
    height: 3px;
    background: var(--bg-gradient-primary);
    border-radius: 0 0 3px 3px;
    transition: transform var(--transition-base);
  }
  
  &:active {
    transform: scale(0.95);
  }
  
  &.active {
    color: var(--primary);
    
    &::before {
      transform: translateX(-50%) scaleX(1);
    }
    
    .nav-icon {
      transform: scale(1.1);
    }
  }
}

.nav-icon {
  font-size: 1.5rem;
  transition: transform var(--transition-base);
}

.nav-label {
  font-size: 0.75rem;
  font-weight: 500;
  line-height: 1;
}
</style>

