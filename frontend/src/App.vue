<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { registerSW } from 'virtual:pwa-register'

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

