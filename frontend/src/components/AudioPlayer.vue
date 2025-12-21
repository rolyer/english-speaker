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
import axios from 'axios'

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

let audio = null
let audioUrl = null

onUnmounted(() => {
  stop()
  cleanup()
})

// 清理资源
function cleanup() {
  if (audio) {
    audio.pause()
    audio = null
  }
  if (audioUrl) {
    URL.revokeObjectURL(audioUrl)
    audioUrl = null
  }
}

// 将 rate (0.5-2.0) 转换为 Edge-TTS 格式 (如 '+0%', '-50%', '+100%')
function convertRate(rate) {
  // Edge-TTS 的 rate 范围是 -50% 到 +100%
  // rate 1.0 = +0%, rate 0.5 = -50%, rate 2.0 = +100%
  const percentage = Math.round((rate - 1.0) * 100)
  const clamped = Math.max(-50, Math.min(100, percentage))
  return clamped >= 0 ? `+${clamped}%` : `${clamped}%`
}

// 将 pitch (0.5-2.0) 转换为 Edge-TTS 格式 (如 '+0Hz', '+5Hz', '-5Hz')
function convertPitch(pitch) {
  // Edge-TTS 的 pitch 范围通常是 -50Hz 到 +50Hz
  // pitch 1.0 = +0Hz, pitch 1.1 ≈ +5Hz, pitch 0.9 ≈ -5Hz
  const hertz = Math.round((pitch - 1.0) * 50)
  const clamped = Math.max(-50, Math.min(50, hertz))
  return clamped >= 0 ? `+${clamped}Hz` : `${clamped}Hz`
}

// 监听text变化，自动播放
watch(() => props.text, (newText, oldText) => {
  // 如果文本变化且之前正在播放，先停止
  if (oldText && isPlaying.value) {
    stop()
  }
  
  // 只有当文本真正改变且不为空时才自动播放
  if (newText && newText !== oldText && props.autoPlay) {
    // 延迟播放，确保DOM已更新
    setTimeout(() => {
      // 再次检查，因为可能在延迟期间用户已经手动播放
      if (props.autoPlay && !isPlaying.value) {
        play()
      }
    }, 300)
  }
}, { immediate: false })

async function play() {
  if (!props.text || !props.text.trim()) {
    ElMessage.warning('没有可播放的文本')
    return
  }
  
  // 停止当前播放
  stop()
  
  loading.value = true
  
  try {
    // 调用后端 TTS API
    const token = localStorage.getItem('token')
    
    const response = await axios.post(
      '/api/tts/synthesize',
      {
        text: props.text,
        language: props.language,
        rate: props.rate !== 1.0 ? convertRate(props.rate) : undefined,
        pitch: props.pitch !== 1.0 ? convertPitch(props.pitch) : undefined
      },
      {
        responseType: 'blob', // 接收二进制数据
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
          'Content-Type': 'application/json'
        }
      }
    )
    
    // 创建音频 URL（blob 数据在 response.data 中）
    audioUrl = URL.createObjectURL(response.data)
    
    // 创建 Audio 对象
    audio = new Audio(audioUrl)
    audio.volume = props.volume
    
    // 设置事件监听
    audio.onplay = () => {
      isPlaying.value = true
      loading.value = false
      emit('play')
    }
    
    audio.onpause = () => {
      isPlaying.value = false
      emit('pause')
    }
    
    audio.onended = () => {
      isPlaying.value = false
      loading.value = false
      emit('end')
      cleanup()
    }
    
    audio.onerror = (event) => {
      console.error('音频播放错误:', event)
      isPlaying.value = false
      loading.value = false
      ElMessage.error('音频播放失败，请重试')
      emit('error', event)
      cleanup()
    }
    
    // 开始播放
    await audio.play()
    
  } catch (error) {
    console.error('播放语音失败:', error)
    loading.value = false
    
    // 处理不同类型的错误
    if (error.response) {
      // API 错误
      const status = error.response.status
      if (status === 401) {
        ElMessage.error('请先登录')
      } else if (status === 400) {
        ElMessage.error(error.response.data?.detail || '请求参数错误')
      } else if (status === 500) {
        ElMessage.error('语音合成服务错误，请稍后重试')
      } else {
        ElMessage.error(`请求失败: ${status}`)
      }
    } else if (error.name === 'NotAllowedError') {
      ElMessage.warning('请允许浏览器播放音频')
    } else {
      ElMessage.error('播放失败，请检查网络连接')
    }
    
    emit('error', error)
    cleanup()
  }
}

function pause() {
  if (audio && isPlaying.value) {
    try {
      audio.pause()
      isPlaying.value = false
      emit('pause')
    } catch (error) {
      console.error('暂停音频时出错:', error)
    }
  }
}

function resume() {
  if (audio && audio.paused && !isPlaying.value) {
    try {
      audio.play()
      isPlaying.value = true
      emit('play')
    } catch (error) {
      console.error('恢复音频时出错:', error)
      // 如果恢复失败，尝试重新播放
      play()
    }
  }
}

function stop() {
  if (audio) {
    try {
      audio.pause()
      audio.currentTime = 0
    } catch (error) {
      console.debug('停止音频时出错:', error)
    }
  }
  
  isPlaying.value = false
  loading.value = false
  cleanup()
}

function togglePlay() {
  if (isPlaying.value) {
    pause()
  } else {
    if (audio && audio.paused) {
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
