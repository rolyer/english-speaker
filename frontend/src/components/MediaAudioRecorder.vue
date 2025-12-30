<template>
  <div class="audio-recorder">
    <div class="record-button-wrapper" :class="{ recording: isRecording }">
      <!-- 波纹效果 -->
      <div v-if="isRecording" class="ripple-container">
        <div class="ripple ripple-1"></div>
        <div class="ripple ripple-2"></div>
        <div class="ripple ripple-3"></div>
      </div>
      
      <!-- 录音按钮 -->
      <el-button
        :type="isRecording ? 'danger' : 'primary'"
        @click="toggleRecording"
        circle
        class="record-button"
      >
        <el-icon :size="mobile ? 28 : 24">
          <component :is="isRecording ? 'VideoPause' : 'Microphone'" />
        </el-icon>
      </el-button>
    </div>
    
    <div v-if="statusMessage" class="status-message" :class="statusType">
      <span>{{ statusMessage }}</span>
    </div>
    
    <div v-if="isRecording" class="recording-text">
      <span>正在录音...</span>
    </div>
    
    <div v-if="transcript" class="transcript">
      <p>{{ transcript }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { isMobile } from '@/utils/device'
import { ElMessage } from 'element-plus'
import { Microphone, VideoPause } from '@element-plus/icons-vue'
import axios from 'axios'

const props = defineProps({
  language: {
    type: String,
    default: 'en-US'
  }
})

const emit = defineEmits(['result', 'error', 'start', 'stop'])

const isRecording = ref(false)
const statusMessage = ref('')
const statusType = ref('info')
const transcript = ref('')
const mobile = computed(() => isMobile())

let mediaRecorder = null
let audioChunks = []
let stream = null

async function toggleRecording() {
  if (isRecording.value) {
    stopRecording()
  } else {
    await startRecording()
  }
}

async function startRecording() {
  try {
    statusMessage.value = '正在请求麦克风权限...'
    statusType.value = 'info'
    
    // 获取麦克风权限
    stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    
    statusMessage.value = '正在启动录音...'
    
    // 创建 MediaRecorder
    const options = { mimeType: 'audio/webm;codecs=opus' }
    mediaRecorder = new MediaRecorder(stream, options)
    
    audioChunks = []
    
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }
    
    mediaRecorder.onstop = async () => {
      statusMessage.value = '正在识别语音...'
      statusType.value = 'info'
      
      try {
        // 创建音频 Blob
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' })
        
        // 发送到后端进行识别
        const formData = new FormData()
        formData.append('file', audioBlob, 'audio.webm')
        formData.append('language', props.language.startsWith('zh') ? 'zh' : 'en')
        
        const token = localStorage.getItem('token')
        const response = await axios.post('/api/stt/transcribe', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${token}`
          }
        })
        
        transcript.value = response.data.text
        emit('result', response.data.text)
        
        statusMessage.value = ''
        ElMessage.success('识别成功')
        
      } catch (error) {
        console.error('语音识别失败:', error)
        statusMessage.value = '识别失败'
        statusType.value = 'error'
        ElMessage.error('语音识别失败: ' + (error.response?.data?.detail || error.message))
        emit('error', error)
      }
      
      // 关闭流
      if (stream) {
        stream.getTracks().forEach(track => track.stop())
        stream = null
      }
    }
    
    mediaRecorder.start()
    isRecording.value = true
    statusMessage.value = ''
    emit('start')
    
  } catch (error) {
    console.error('启动录音失败:', error)
    statusMessage.value = '启动失败'
    statusType.value = 'error'
    
    if (error.name === 'NotAllowedError') {
      ElMessage.error('麦克风权限被拒绝')
    } else {
      ElMessage.error('启动录音失败: ' + error.message)
    }
    
    emit('error', error)
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
  }
  isRecording.value = false
  emit('stop', transcript.value)
}
</script>

<style lang="scss" scoped>
.audio-recorder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.record-button-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &.recording {
    .record-button {
      animation: pulse 1.5s ease-in-out infinite;
    }
  }
}

.ripple-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
}

.ripple {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 2px solid var(--el-color-danger);
  opacity: 0;
  animation: ripple-animation 2s infinite;
  
  @media (max-width: 768px) {
    width: 90px;
    height: 90px;
  }
  
  &.ripple-1 {
    animation-delay: 0s;
  }
  
  &.ripple-2 {
    animation-delay: 0.6s;
  }
  
  &.ripple-3 {
    animation-delay: 1.2s;
  }
}

@keyframes ripple-animation {
  0% {
    transform: translate(-50%, -50%) scale(0.8);
    opacity: 1;
  }
  100% {
    transform: translate(-50%, -50%) scale(2.5);
    opacity: 0;
  }
}

.record-button {
  width: 80px;
  height: 80px;
  font-size: 24px;
  transition: all 0.3s ease;
  z-index: 1;
  
  @media (max-width: 768px) {
    width: 90px;
    height: 90px;
    font-size: 28px;
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.status-message {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  
  &.info {
    background: #e1f3fb;
    color: #0288d1;
  }
  
  &.success {
    background: #e8f5e9;
    color: #4caf50;
  }
  
  &.error {
    background: #ffebee;
    color: #f44336;
  }
}

.recording-text {
  color: var(--el-color-danger);
  font-weight: 500;
  animation: blink 1.5s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.transcript {
  max-width: 600px;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 8px;
  
  p {
    margin: 0;
    line-height: 1.6;
  }
}
</style>

