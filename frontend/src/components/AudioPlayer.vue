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
watch(() => props.text, (newText, oldText) => {
  // 只有当文本真正改变且不为空时才自动播放
  if (newText && newText !== oldText && props.autoPlay && isSupported.value) {
    // 延迟播放，确保DOM已更新
    setTimeout(() => {
      // 再次检查，因为可能在延迟期间用户已经手动播放
      if (props.autoPlay && !isPlaying.value) {
        play()
      }
    }, 300)
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
    loading.value = false
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
        errorMessage = '语音合成失败，请重试'
        break
      case 'synthesis-unavailable':
        errorMessage = '语音合成服务不可用'
        break
      case 'interrupted':
        errorMessage = '语音播放被中断'
        break
      case 'canceled':
        // 用户取消，不显示错误
        return
      default:
        errorMessage = `语音播放失败: ${event.error || '未知错误'}`
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
  
  try {
    synth = window.speechSynthesis
    
    // 某些浏览器需要取消之前的语音才能播放新的
    synth.cancel()
    
    // 等待一小段时间确保浏览器准备好
    setTimeout(() => {
      utterance = createUtterance()
      
      if (utterance) {
        try {
          synth.speak(utterance)
          
          // 设置超时，如果5秒内没有开始播放，认为失败
          const timeoutId = setTimeout(() => {
            if (loading.value && !isPlaying.value) {
              loading.value = false
              ElMessage.error('语音播放超时，请重试')
              emit('error', 'timeout')
            }
          }, 5000)
          
          // 如果开始播放，清除超时
          const originalOnstart = utterance.onstart
          utterance.onstart = () => {
            clearTimeout(timeoutId)
            if (originalOnstart) originalOnstart()
          }
        } catch (error) {
          console.error('播放语音时出错:', error)
          loading.value = false
          ElMessage.error('语音播放失败，请重试')
          emit('error', error)
        }
      } else {
        loading.value = false
      }
    }, 100)
  } catch (error) {
    console.error('初始化语音合成时出错:', error)
    loading.value = false
    ElMessage.error('语音播放失败，请重试')
    emit('error', error)
  }
}

function pause() {
  if (synth && (isPlaying.value || synth.speaking)) {
    try {
      synth.pause()
      isPlaying.value = false
      emit('pause')
    } catch (error) {
      console.error('暂停语音时出错:', error)
    }
  }
}

function resume() {
  if (synth && synth.paused && !isPlaying.value) {
    try {
      synth.resume()
      isPlaying.value = true
      emit('play')
    } catch (error) {
      console.error('恢复语音时出错:', error)
      // 如果恢复失败，尝试重新播放
      play()
    }
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

