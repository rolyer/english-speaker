<template>
  <div id="app">
    <Layout v-if="showLayout" />
    <router-view v-else />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { registerSW } from 'virtual:pwa-register'
import Layout from '@/components/Layout.vue'

const route = useRoute()

// 登录和注册页面不显示导航栏
const showLayout = computed(() => {
  return route.name !== 'Login' && route.name !== 'Register'
})

onMounted(() => {
  // 注册Service Worker
  if ('serviceWorker' in navigator) {
    registerSW({
      immediate: true
    })
  }
})
</script>

<style lang="scss">
#app {
  width: 100%;
  min-height: 100vh;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}
</style>

