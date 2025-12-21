<template>
  <div class="audio-player">
    <el-button
      :type="isPlaying ? 'warning' : 'primary'"
      :icon="isPlaying ? 'VideoPause' : 'VideoPlay'"
      :loading="loading"
      @click="togglePlay"
      :size="mobile ? 'default' : 'small'"
      circle
      class="play-button"
    />
    
    <div v-if="isPlaying" class="playing-indicator">
      <span>正在播放...</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted, watch } from 'vue'
import { isMobile } from '@/utils/device'
import { ElMessage } from 'element-plus'

const props = defineProps({
  text: {
    type: String,
    default: ''
  },
  language: {
    type: String,
    default: 'en-US'
  },
  rate: {
    type: Number,
    default: 1.0
  },
  pitch: {
    type: Number,
    default: 1.0
  },
  volume: {
    type: Number,
    default: 1.0
  },
  autoPlay: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['play', 'pause', 'end', 'error'])

const isPlaying = ref(false)
const loading = ref(false)
const mobile = computed(() => isMobile())

let synth = null
let utterance = null

onUnmounted(() => {
  stop()
})

// 检查浏览器支持
const isSupported = computed(() => {
  return 'speechSynthesis' in window
})

// 监听text变化，自动播放
watch(() => props.text, (newText) => {
  if (newText && props.autoPlay && isSupported.value) {
    play()
  }
}, { immediate: false })

function createUtterance() {
  if (!isSupported.value) {
    ElMessage.warning('您的浏览器不支持语音合成功能')
    return null
  }
  
  const utterance = new SpeechSynthesisUtterance(props.text)
  utterance.lang = props.language
  utterance.rate = props.rate
  utterance.pitch = props.pitch
  utterance.volume = props.volume
  
  utterance.onstart = () => {
    isPlaying.value = true
    loading.value = false
    emit('play')
  }
  
  utterance.onend = () => {
    isPlaying.value = false
    emit('end')
  }
  
  utterance.onerror = (event) => {
    console.error('语音合成错误:', event.error)
    isPlaying.value = false
    loading.value = false
    
    let errorMessage = '语音播放失败'
    switch (event.error) {
      case 'network':
        errorMessage = '网络错误，请检查网络连接'
        break
      case 'synthesis-failed':
        errorMessage = '语音合成失败'
        break
      case 'synthesis-unavailable':
        errorMessage = '语音合成服务不可用'
        break
    }
    
    ElMessage.error(errorMessage)
    emit('error', event.error)
  }
  
  return utterance
}

function play() {
  if (!props.text) {
    ElMessage.warning('没有可播放的文本')
    return
  }
  
  if (!isSupported.value) {
    ElMessage.warning('您的浏览器不支持语音合成')
    return
  }
  
  // 停止当前播放
  stop()
  
  loading.value = true
  utterance = createUtterance()
  
  if (utterance) {
    synth = window.speechSynthesis
    synth.speak(utterance)
  }
}

function pause() {
  if (synth && isPlaying.value) {
    synth.pause()
    isPlaying.value = false
    emit('pause')
  }
}

function resume() {
  if (synth && !isPlaying.value) {
    synth.resume()
    isPlaying.value = true
    emit('play')
  }
}

function stop() {
  if (synth) {
    synth.cancel()
    isPlaying.value = false
    loading.value = false
    utterance = null
  }
}

function togglePlay() {
  if (isPlaying.value) {
    pause()
  } else {
    if (synth && synth.paused) {
      resume()
    } else {
      play()
    }
  }
}

// 暴露方法供父组件调用
defineExpose({
  play,
  pause,
  resume,
  stop,
  togglePlay
})
</script>

<style lang="scss" scoped>
.audio-player {
  display: flex;
  align-items: center;
  gap: 12px;
}

.play-button {
  min-width: 40px;
  min-height: 40px;
  
  @media (max-width: 768px) {
    min-width: 44px;
    min-height: 44px;
  }
}

.playing-indicator {
  color: var(--primary-color);
  font-size: 0.9rem;
  
  @media (max-width: 768px) {
    font-size: 0.85rem;
  }
}
</style>

