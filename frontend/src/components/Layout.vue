<template>
  <div class="layout">
    <NavBar />
    <main class="main-content" :class="{ 'with-mobile-nav': mobile }">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { isMobile } from '@/utils/device'
import NavBar from './NavBar.vue'

const mobile = computed(() => isMobile())
</script>

<style lang="scss" scoped>
.layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  width: 100%;
  
  &.with-mobile-nav {
    padding-bottom: 60px; // 为移动端底部导航栏留出空间
  }
}
</style>

