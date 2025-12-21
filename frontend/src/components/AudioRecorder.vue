<template>
  <div class="audio-recorder">
    <el-button
      :type="isRecording ? 'danger' : 'primary'"
      :icon="isRecording ? 'VideoPause' : 'Microphone'"
      :loading="loading"
      :disabled="!isSupported"
      @click="toggleRecording"
      :size="mobile ? 'large' : 'default'"
      circle
      class="record-button"
    >
      <span v-if="!isRecording && !loading">录音</span>
      <span v-else-if="isRecording">停止</span>
    </el-button>
    
    <div v-if="isRecording" class="recording-indicator">
      <div class="pulse"></div>
      <span>正在录音...</span>
    </div>
    
    <div v-if="transcript" class="transcript">
      <p>{{ transcript }}</p>
    </div>
    
    <el-dialog
      v-model="showPermissionDialog"
      title="需要麦克风权限"
      width="90%"
      :close-on-click-modal="false"
    >
      <p>为了使用语音功能，需要访问您的麦克风。</p>
      <p>请点击"允许"以继续。</p>
      <template #footer>
        <el-button @click="showPermissionDialog = false">取消</el-button>
        <el-button type="primary" @click="requestPermission">允许</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { isSpeechRecognitionSupported, getSpeechRecognition, requestMicrophonePermission, isIOSDevice } from '@/utils/mobileAudio'
import { isMobile } from '@/utils/device'
import { ElMessage } from 'element-plus'

const props = defineProps({
  language: {
    type: String,
    default: 'en-US'
  },
  continuous: {
    type: Boolean,
    default: false
  },
  interimResults: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['result', 'error', 'start', 'stop'])

const isRecording = ref(false)
const loading = ref(false)
const transcript = ref('')
const isSupported = ref(false)
const showPermissionDialog = ref(false)
const mobile = computed(() => isMobile())

let recognition = null

onMounted(() => {
  isSupported.value = isSpeechRecognitionSupported()
  if (isSupported.value) {
    recognition = getSpeechRecognition()
    if (recognition) {
      setupRecognition()
    }
  } else {
    ElMessage.warning('您的浏览器不支持语音识别功能')
  }
})

onUnmounted(() => {
  if (recognition && isRecording.value) {
    recognition.stop()
  }
})

function setupRecognition() {
  if (!recognition) return
  
  recognition.lang = props.language
  recognition.continuous = props.continuous
  recognition.interimResults = props.interimResults
  
  recognition.onstart = () => {
    isRecording.value = true
    transcript.value = ''
    emit('start')
  }
  
  recognition.onresult = (event) => {
    let interimTranscript = ''
    let finalTranscript = ''
    
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript
      if (event.results[i].isFinal) {
        finalTranscript += transcript + ' '
      } else {
        interimTranscript += transcript
      }
    }
    
    transcript.value = finalTranscript || interimTranscript
    
    if (finalTranscript) {
      emit('result', finalTranscript.trim())
    }
  }
  
  recognition.onerror = (event) => {
    console.error('语音识别错误:', event.error)
    
    let errorMessage = '语音识别失败'
    switch (event.error) {
      case 'no-speech':
        errorMessage = '未检测到语音，请重试'
        break
      case 'audio-capture':
        errorMessage = '无法访问麦克风'
        showPermissionDialog.value = true
        break
      case 'not-allowed':
        errorMessage = '麦克风权限被拒绝'
        showPermissionDialog.value = true
        break
      case 'network':
        errorMessage = '网络错误，请检查网络连接'
        break
    }
    
    ElMessage.error(errorMessage)
    emit('error', event.error)
    stopRecording()
  }
  
  recognition.onend = () => {
    if (isRecording.value && props.continuous) {
      // 如果设置了连续模式，自动重新开始
      try {
        recognition.start()
      } catch (e) {
        stopRecording()
      }
    } else {
      stopRecording()
    }
  }
}

async function toggleRecording() {
  if (!isSupported.value) {
    ElMessage.warning('您的浏览器不支持语音识别')
    return
  }
  
  if (isRecording.value) {
    stopRecording()
  } else {
    await startRecording()
  }
}

async function startRecording() {
  // iOS需要用户交互才能启动
  if (isIOSDevice()) {
    const hasPermission = await requestMicrophonePermission()
    if (!hasPermission) {
      showPermissionDialog.value = true
      return
    }
  }
  
  if (!recognition) {
    ElMessage.error('语音识别未初始化')
    return
  }
  
  try {
    loading.value = true
    recognition.start()
  } catch (error) {
    console.error('启动录音失败:', error)
    ElMessage.error('启动录音失败，请重试')
    loading.value = false
  }
}

function stopRecording() {
  if (recognition && isRecording.value) {
    try {
      recognition.stop()
    } catch (e) {
      console.error('停止录音失败:', e)
    }
  }
  isRecording.value = false
  loading.value = false
  emit('stop', transcript.value)
}

async function requestPermission() {
  showPermissionDialog.value = false
  const granted = await requestMicrophonePermission()
  if (granted) {
    ElMessage.success('权限已授予')
    await startRecording()
  } else {
    ElMessage.error('权限被拒绝，无法使用语音功能')
  }
}
</script>

<style lang="scss" scoped>
.audio-recorder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.record-button {
  width: 64px;
  height: 64px;
  font-size: 18px;
  
  @media (max-width: 768px) {
    width: 72px;
    height: 72px;
    font-size: 20px;
  }
}

.recording-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--primary-color);
  font-weight: 500;
  
  .pulse {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--primary-color);
    animation: pulse 1.5s infinite;
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
}

.transcript {
  max-width: 100%;
  padding: 12px;
  background: var(--bg-light);
  border-radius: 8px;
  min-height: 40px;
  
  p {
    margin: 0;
    color: var(--text-color);
    line-height: 1.6;
  }
}
</style>

