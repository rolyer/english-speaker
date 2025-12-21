<template>
  <div class="home">
    <div class="hero-section">
      <h1 class="title">🎉 欢迎来到英语口语训练</h1>
      <p class="subtitle">和AI老师一起练习英语口语吧！</p>
      <div class="actions">
        <el-button
          v-if="!userStore.isAuthenticated"
          type="primary"
          size="large"
          @click="$router.push('/login')"
        >
          开始学习
        </el-button>
        <el-button
          v-else
          type="primary"
          size="large"
          @click="$router.push('/conversation')"
        >
          开始对话
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
</script>

<style lang="scss" scoped>
.home {
  min-height: calc(100vh - 64px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #ff6b9d 0%, #4ecdc4 100%);
  padding: 20px;
  
  @media (max-width: 768px) {
    min-height: calc(100vh - 60px);
  }
}

.hero-section {
  text-align: center;
  color: white;
  max-width: 600px;
  
  .title {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    font-weight: bold;
    
    @media (max-width: 768px) {
      font-size: 2rem;
    }
  }
  
  .subtitle {
    font-size: 1.2rem;
    margin-bottom: 2rem;
    opacity: 0.9;
    
    @media (max-width: 768px) {
      font-size: 1rem;
    }
  }
  
  .actions {
    margin-top: 2rem;
  }
}
</style>

