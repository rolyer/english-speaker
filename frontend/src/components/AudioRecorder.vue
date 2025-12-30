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
        :disabled="!isSupported"
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
    
    <!-- 调试信息显示 -->
    <div v-if="showDebug" class="debug-panel">
      <div class="debug-header">
        <strong>调试信息 ({{ debugInfo.length }} 条)</strong>
        <div class="debug-actions">
          <button @click="copyLogs" style="margin-left: 5px; padding: 2px 8px;">复制</button>
          <button @click="clearLogs" style="margin-left: 5px; padding: 2px 8px;">清空</button>
          <button @click="showDebug = false" style="margin-left: 5px; padding: 2px 8px;">隐藏</button>
        </div>
      </div>
      <div class="debug-status">
        <div><strong>isRecording:</strong> {{ isRecording ? '✅ true' : '❌ false' }}</div>
        <div><strong>isSupported:</strong> {{ isSupported ? '✅ true' : '❌ false' }}</div>
        <div><strong>continuous:</strong> {{ recognition?.continuous ? '✅ true' : '❌ false' }}</div>
        <div><strong>isAndroid:</strong> {{ isAndroid ? '✅ true' : '❌ false' }}</div>
        <div><strong>lang:</strong> {{ recognition?.lang || 'N/A' }}</div>
        <div><strong>interimResults:</strong> {{ recognition?.interimResults ? 'true' : 'false' }}</div>
      </div>
      <div class="debug-logs">
        <div v-for="(log, index) in debugInfo" :key="index" class="debug-log">
          {{ log }}
        </div>
      </div>
    </div>
    <button v-else @click="showDebug = true" class="show-debug-btn">显示调试信息</button>
    
    <div v-if="isRecording" class="recording-text">
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
      <p v-if="isAndroid">
        请点击下方"允许"按钮，然后在浏览器弹出的权限对话框中点击"允许"。
        <br>
        如果权限已被拒绝，请前往浏览器设置中允许麦克风权限。
      </p>
      <p v-else>请点击"允许"以继续。</p>
      <template #footer>
        <el-button @click="showPermissionDialog = false">取消</el-button>
        <el-button type="primary" @click="requestPermission">允许</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { isSpeechRecognitionSupported, getSpeechRecognition, requestMicrophonePermission, isIOSDevice, isAndroidDevice } from '@/utils/mobileAudio'
import { isMobile } from '@/utils/device'
import { ElMessage } from 'element-plus'
import { Microphone, VideoPause } from '@element-plus/icons-vue'

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
const statusMessage = ref('')
const statusType = ref('info') // 'info', 'success', 'error', 'warning'
const mobile = computed(() => isMobile())
const isAndroid = computed(() => isAndroidDevice())

// 调试信息
const debugInfo = ref([])
const showDebug = ref(true)

let recognition = null
let originalOnStart = null
let shouldClearStatusOnStart = true // 标志位：是否在 onstart 时清空状态消息
let isStarting = false // 标志位：是否正在启动中（用于忽略启动阶段的 onend）
let activeStream = null // 保存活动的 media stream，在录音结束时才关闭
let onStartCallback = null // Android 流程的 onstart 回调
let isAutoRestarting = false // 标志位：是否正在自动重启（用于 Android aborted 错误恢复）

// MediaRecorder 备用方案
let mediaRecorder = null
let audioChunks = []
let useMediaRecorder = false // 是否使用 MediaRecorder 备用方案

// 添加调试日志
function addDebugLog(message) {
  const timestamp = new Date().toLocaleTimeString()
   // 只保留最后10条
  // if (debugInfo.value.length > 10) {
  //   debugInfo.value.shift()
  // }
  debugInfo.value.push(`[${timestamp}] ${message}`)
  // 不再限制日志条数，保留所有日志
  console.log('[AudioRecorder]', message)
}

// 复制日志到剪贴板
function copyLogs() {
  const logs = debugInfo.value.join('\n')
  navigator.clipboard.writeText(logs).then(() => {
    ElMessage.success('日志已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败，请手动复制')
  })
}

// 清空日志
function clearLogs() {
  debugInfo.value = []
  ElMessage.info('日志已清空')
}

onMounted(() => {
  addDebugLog('组件 onMounted')
  isSupported.value = isSpeechRecognitionSupported()
  addDebugLog(`isSpeechRecognitionSupported: ${isSupported.value}`)
  if (isSupported.value) {
    recognition = getSpeechRecognition()
    addDebugLog(`getSpeechRecognition: ${recognition ? '成功' : '失败'}`)
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
  addDebugLog('setupRecognition 开始')
  if (!recognition) {
    addDebugLog('recognition 为 null，退出')
    return
  }
  
  addDebugLog(`初始状态: isRecording=${isRecording.value}, isStarting=${isStarting}, isAutoRestarting=${isAutoRestarting}`)
  
  recognition.lang = props.language
  // Android 设备强制使用 continuous 模式，避免快速中断
  recognition.continuous = isAndroidDevice() ? true : props.continuous
  recognition.interimResults = props.interimResults
  
  addDebugLog(`setupRecognition: lang=${props.language}, continuous=${recognition.continuous}, interimResults=${props.interimResults}`)
  
  originalOnStart = () => {
    addDebugLog('originalOnStart 执行')
    isRecording.value = true
    addDebugLog('isRecording 设置为 true')
    transcript.value = ''
    emit('start')
  }
  
  recognition.onstart = () => {
    addDebugLog(`setupRecognition onstart 触发, shouldClear: ${shouldClearStatusOnStart}`)
    addDebugLog(`recognition 配置: lang=${recognition.lang}, continuous=${recognition.continuous}, interimResults=${recognition.interimResults}`)
    originalOnStart()
    addDebugLog(`originalOnStart 后, isRecording: ${isRecording.value}`)
    
    // 如果有 Android 流程的回调，执行它
    if (onStartCallback) {
      addDebugLog('执行 onStartCallback')
      onStartCallback()
      onStartCallback = null // 执行后清空
    }
    
    // 只有在标志位为 true 时才清空状态消息
    if (shouldClearStatusOnStart) {
      statusMessage.value = ''
    }
  }
  
  recognition.onresult = (event) => {
    addDebugLog('onresult 触发')
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
    addDebugLog(`识别结果: ${transcript.value.substring(0, 20)}...`)
    
    if (finalTranscript) {
      emit('result', finalTranscript.trim())
    }
  }
  
  recognition.onerror = (event) => {
    addDebugLog('onerror 触发: ' + event.error)
    
    let errorMessage = '语音识别失败'
    switch (event.error) {
      case 'no-speech':
        errorMessage = '未检测到语音，请重试'
        addDebugLog('未检测到语音')
        // 不停止录音，让用户继续说话
        return
      case 'audio-capture':
        errorMessage = '无法访问麦克风'
        addDebugLog('无法访问麦克风')
        showPermissionDialog.value = true
        break
      case 'not-allowed':
        errorMessage = '麦克风权限被拒绝'
        addDebugLog('麦克风权限被拒绝')
        showPermissionDialog.value = true
        break
      case 'network':
        errorMessage = '网络错误，请检查网络连接'
        addDebugLog('网络错误')
        break
      case 'aborted':
        // Android Chrome 的 aborted 错误处理
        addDebugLog(`识别被中断 (isAndroid: ${isAndroidDevice()}, isRecording: ${isRecording.value}, isAutoRestarting: ${isAutoRestarting})`)
        // 如果是 Android 设备且正在录音，尝试自动重启
        if (isAndroidDevice() && isRecording.value && !isAutoRestarting) {
          addDebugLog(`Android 设备，尝试自动重启识别 (isStarting: ${isStarting})`)
          isAutoRestarting = true
          addDebugLog('设置 isAutoRestarting = true')
          setTimeout(() => {
            addDebugLog(`延迟后检查: isRecording=${isRecording.value}`)
            if (isRecording.value) {
              try {
                addDebugLog('调用 recognition.start() 重启')
                recognition.start()
                addDebugLog('自动重启调用成功')
                // 重启成功后，重置标志
                setTimeout(() => {
                  isAutoRestarting = false
                  isStarting = false
                  addDebugLog('重置 isAutoRestarting 和 isStarting 标志')
                }, 1000)
              } catch (e) {
                addDebugLog('自动重启失败: ' + e.message)
                isAutoRestarting = false
                ElMessage.error('语音识别启动失败，请重试')
                stopRecording()
              }
            } else {
              addDebugLog('isRecording 已为 false，取消重启')
              isAutoRestarting = false
            }
          }, 200)
          return
        } else {
          addDebugLog(`不满足自动重启条件: isAndroid=${isAndroidDevice()}, isRecording=${isRecording.value}, isAutoRestarting=${isAutoRestarting}`)
        }
        return
      default:
        errorMessage = `语音识别失败: ${event.error}`
        addDebugLog('其他错误: ' + event.error)
    }
    
    ElMessage.error(errorMessage)
    emit('error', event.error)
    stopRecording()
  }
  
  recognition.onend = () => {
    addDebugLog(`onend 触发, isRecording: ${isRecording.value}, continuous: ${recognition.continuous}, isStarting: ${isStarting}, isAutoRestarting: ${isAutoRestarting}`)
    
    // 如果正在启动中或正在自动重启，忽略 onend 事件
    if (isStarting || isAutoRestarting) {
      addDebugLog('正在启动/重启中，忽略 onend 事件')
      return
    }
    
    if (isRecording.value && recognition.continuous) {
      // 如果设置了连续模式，自动重新开始
      addDebugLog('连续模式，尝试重新启动')
      try {
        recognition.start()
        addDebugLog('重新启动成功')
      } catch (e) {
        addDebugLog('重新启动失败: ' + e.message)
        stopRecording()
      }
    } else {
      addDebugLog('停止录音')
      stopRecording()
    }
  }
}

async function toggleRecording() {
  try {
    addDebugLog('toggleRecording 点击')
    if (!isSupported.value) {
      addDebugLog('浏览器不支持语音识别')
      ElMessage.warning('您的浏览器不支持语音识别')
      return
    }
    
    if (isRecording.value) {
      addDebugLog('停止录音')
      stopRecording()
    } else {
      addDebugLog('开始录音')
      await startRecording()
    }
  } catch (error) {
    addDebugLog('错误: ' + (error.message || error.name))
    statusMessage.value = '发生错误: ' + (error.message || error.name)
    statusType.value = 'error'
    ElMessage.error('录音功能出错: ' + (error.message || error.name))
  }
}

async function startRecording() {
  try {
    statusMessage.value = '正在初始化...'
    statusType.value = 'info'
    
    if (!recognition) {
      statusMessage.value = '语音识别未初始化'
      statusType.value = 'error'
      ElMessage.error('语音识别未初始化')
      return
    }
    
    // Android Chrome: 直接启动 SpeechRecognition，让它自己处理麦克风权限
    if (isAndroidDevice()) {
      addDebugLog(`Android 设备，直接启动 SpeechRecognition (isAutoRestarting初始值: ${isAutoRestarting})`)
      
      // 确保标志位初始状态正确
      isAutoRestarting = false
      addDebugLog('重置 isAutoRestarting = false')
      
      // 设置标志位，防止 setupRecognition 中的 onstart 清空状态消息
      shouldClearStatusOnStart = false
      
      // 设置启动标志，防止启动阶段的 onend 事件触发 stopRecording
      isStarting = true
      addDebugLog('设置 isStarting = true')
      
      // 设置 onstart 回调函数
      onStartCallback = () => {
        addDebugLog('Android onStartCallback 执行')
        
        addDebugLog(`onstart 后 isRecording: ${isRecording.value}`)
        
        // 显示录音已开始的状态
        statusMessage.value = '正在录音...'
        statusType.value = 'success'
        
        // 清除启动标志，允许后续的 onend 事件正常处理
        setTimeout(() => {
          isStarting = false
          addDebugLog('清除 isStarting 标志')
        }, 1000)
        
        // 延迟清空状态消息，让用户看到录音已开始
        setTimeout(() => {
          statusMessage.value = ''
          // 恢复标志位
          shouldClearStatusOnStart = true
        }, 2000)
      }
      
      // 启动语音识别
      statusMessage.value = '正在启动语音识别...'
      statusType.value = 'info'
      addDebugLog('调用 recognition.start()')
      
      try {
        recognition.start()
        addDebugLog('recognition.start() 调用成功')
      } catch (startError) {
        addDebugLog('recognition.start() 失败: ' + startError.message)
        statusMessage.value = '启动失败: ' + (startError.message || startError.name)
        statusType.value = 'error'
        isStarting = false
        onStartCallback = null
        shouldClearStatusOnStart = true
        
        if (startError.name === 'NotAllowedError' || startError.name === 'PermissionDeniedError') {
          showPermissionDialog.value = true
          ElMessage.error('麦克风权限被拒绝，请允许权限后重试')
        } else {
          ElMessage.error('启动失败: ' + (startError.message || startError.name))
        }
        return
      }
      
      return
    }
    
    // iOS需要先请求权限
    if (isIOSDevice()) {
      const hasPermission = await requestMicrophonePermission()
      if (!hasPermission) {
        showPermissionDialog.value = true
        return
      }
    }
    
    // 其他平台直接启动
    statusMessage.value = '正在启动语音识别...'
    statusType.value = 'info'
    try {
      recognition.start()
    } catch (error) {
      statusMessage.value = '启动失败: ' + (error.message || error.name)
      statusType.value = 'error'
      if (error.name === 'NotAllowedError' || error.message?.includes('permission')) {
        showPermissionDialog.value = true
        ElMessage.error('需要麦克风权限才能使用语音功能')
      } else {
        ElMessage.error('启动录音失败: ' + (error.message || error.name))
      }
    }
  } catch (error) {
    console.error('startRecording 错误:', error)
    statusMessage.value = '启动失败: ' + (error.message || error.name)
    statusType.value = 'error'
    ElMessage.error('启动录音失败: ' + (error.message || error.name))
  }
}

function stopRecording() {
  addDebugLog('stopRecording 调用')
  
  if (useMediaRecorder && mediaRecorder) {
    // 使用 MediaRecorder 方案
    addDebugLog('停止 MediaRecorder')
    try {
      if (mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop()
      }
    } catch (e) {
      addDebugLog('MediaRecorder.stop() 失败: ' + e.message)
    }
  } else if (recognition && isRecording.value) {
    // 使用 SpeechRecognition 方案
    try {
      recognition.stop()
      addDebugLog('recognition.stop() 成功')
    } catch (e) {
      addDebugLog('recognition.stop() 失败: ' + e.message)
    }
  }
  
  // 关闭活动的 media stream
  if (activeStream) {
    addDebugLog('关闭 activeStream')
    activeStream.getTracks().forEach(track => track.stop())
    activeStream = null
  }
  
  isRecording.value = false
  isStarting = false // 清除启动标志
  isAutoRestarting = false // 清除自动重启标志
  statusMessage.value = ''
  addDebugLog('isRecording 设置为 false')
  emit('stop', transcript.value)
}

async function requestPermission() {
  showPermissionDialog.value = false
  
  // Android Chrome 需要在用户交互事件中直接请求权限
  if (isAndroidDevice()) {
    if (!recognition) {
      ElMessage.error('语音识别未初始化')
      return
    }
    
    // 检查权限状态（如果浏览器支持 Permissions API）
    let permissionStatus = null
    if (navigator.permissions && navigator.permissions.query) {
      try {
        permissionStatus = await navigator.permissions.query({ name: 'microphone' })
        console.log('当前权限状态:', permissionStatus.state)
        
        // 如果权限已经被拒绝，提示用户到浏览器设置中修改
        if (permissionStatus.state === 'denied') {
          ElMessage.error({
            message: '权限已被拒绝。请前往浏览器设置 → 网站设置 → 麦克风，允许此网站的麦克风权限，然后刷新页面。',
            duration: 6000,
            showClose: true
          })
          return
        }
      } catch (e) {
        // Permissions API 可能不支持，继续尝试请求权限
        console.log('Permissions API 不支持，继续请求权限')
      }
    }
    
    try {
      // 在用户交互事件中直接请求权限
      // 这会触发浏览器的权限弹窗（如果权限还未授予）
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      
      // 权限已授予，停止流（我们只需要权限，不需要实际的音频流）
      stream.getTracks().forEach(track => track.stop())
      
      // 权限授予后，延迟一小段时间再启动 SpeechRecognition
      // 确保权限状态已完全更新
      statusMessage.value = '权限已授予，正在启动录音...'
      statusType.value = 'success'
      ElMessage.success('权限已授予')
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // 现在启动语音识别
      try {
        statusMessage.value = '正在启动语音识别...'
        statusType.value = 'info'
        recognition.start()
        
        // 设置超时检查，如果 2 秒内没有触发 onstart，认为启动失败
        const startTimeout = setTimeout(() => {
          if (!isRecording.value) {
            statusMessage.value = '语音识别启动超时'
            statusType.value = 'error'
            ElMessage.error('语音识别启动超时，请重试')
          }
        }, 2000)
        
        // 监听 onstart 事件，成功后清除超时
        const currentOnStart = recognition.onstart
        recognition.onstart = () => {
          clearTimeout(startTimeout)
          statusMessage.value = ''
          // 调用原始的 onstart 处理函数
          if (currentOnStart) {
            currentOnStart()
          }
        }
        
        // 如果成功，onstart 事件会设置 isRecording = true
        // 不需要显示成功消息，因为录音已经开始
      } catch (startError) {
        statusMessage.value = '启动失败: ' + (startError.message || startError.name)
        statusType.value = 'error'
        // 如果启动失败，可能是权限问题或其他错误
        if (startError.name === 'NotAllowedError' || startError.name === 'AbortError') {
          ElMessage.error('语音识别启动失败，请重试')
          // 不显示对话框，让用户再次点击录音按钮
        } else {
          ElMessage.error('无法启动语音识别: ' + (startError.message || startError.name))
        }
      }
      return
    } catch (error) {
      console.error('麦克风权限请求失败:', error)
      
      // 根据错误类型提供不同的提示
      if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
        ElMessage.error({
          message: '权限被拒绝。请在浏览器设置中允许麦克风权限，然后刷新页面重试。',
          duration: 5000,
          showClose: true
        })
        // 不重新显示对话框，因为用户已经拒绝过
      } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
        ElMessage.error('未找到麦克风设备，请检查设备连接')
      } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
        ElMessage.error('麦克风被其他应用占用，请关闭其他应用后重试')
      } else {
        ElMessage.error('无法访问麦克风: ' + (error.message || error.name))
        // 对于未知错误，重新显示对话框让用户重试
        showPermissionDialog.value = true
      }
      return
    }
  }
  
  // iOS 和其他平台
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

.record-button-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &.recording {
    .record-button {
      box-shadow: 0 0 0 4px rgba(245, 108, 108, 0.2);
    }
  }
}

.ripple-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  height: 100%;
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

.debug-panel {
  position: fixed;
  top: 60px;
  right: 10px;
  width: 90%;
  max-width: 400px;
  max-height: 400px;
  background: rgba(0, 0, 0, 0.9);
  color: #0f0;
  padding: 10px;
  border-radius: 8px;
  font-family: monospace;
  font-size: 12px;
  z-index: 9999;
  overflow: hidden;
  
  @media (max-width: 768px) {
    top: 10px;
    right: 10px;
    left: 10px;
    width: auto;
    max-width: none;
  }
}

.debug-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 5px;
  border-bottom: 1px solid #0f0;
  
  strong {
    color: #0ff;
  }
  
  .debug-actions {
    display: flex;
    gap: 5px;
  }
  
  button {
    background: #333;
    color: #fff;
    border: 1px solid #0f0;
    border-radius: 4px;
    cursor: pointer;
    font-size: 10px;
    padding: 2px 8px;
    
    &:hover {
      background: #444;
    }
    
    &:active {
      background: #222;
    }
  }
}

.debug-status {
  margin-bottom: 10px;
  padding: 5px;
  background: rgba(0, 255, 0, 0.1);
  border-radius: 4px;
  
  div {
    margin: 3px 0;
    
    strong {
      color: #ff0;
    }
  }
}

.debug-logs {
  max-height: 250px;
  overflow-y: auto;
  padding: 5px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 4px;
}

.debug-log {
  margin: 2px 0;
  padding: 2px 5px;
  border-left: 2px solid #0f0;
  word-break: break-all;
}

.show-debug-btn {
  position: fixed;
  top: 70px;
  right: 10px;
  padding: 5px 10px;
  background: rgba(0, 0, 0, 0.7);
  color: #0f0;
  border: 1px solid #0f0;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  z-index: 9999;
  
  @media (max-width: 768px) {
    top: 20px;
  }
}

.record-button {
  width: 80px;
  height: 80px;
  font-size: 24px;
  transition: all 0.3s ease;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  
  @media (max-width: 768px) {
    width: 90px;
    height: 90px;
    font-size: 28px;
  }
  
  &:hover {
    transform: scale(1.05);
  }
  
  &:active {
    transform: scale(0.95);
  }
  
  // 确保图标居中
  :deep(.el-icon) {
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.status-message {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
  min-height: 32px;
  
  &.info {
    background-color: #e6f7ff;
    color: #1890ff;
    border: 1px solid #91d5ff;
  }
  
  &.success {
    background-color: #f6ffed;
    color: #52c41a;
    border: 1px solid #b7eb8f;
  }
  
  &.error {
    background-color: #fff2f0;
    color: #ff4d4f;
    border: 1px solid #ffccc7;
  }
  
  &.warning {
    background-color: #fffbe6;
    color: #faad14;
    border: 1px solid #ffe58f;
  }
  
  @media (max-width: 768px) {
    font-size: 13px;
    padding: 6px 12px;
  }
}

.recording-text {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--el-color-danger);
  font-weight: 500;
  font-size: 14px;
  animation: pulse-text 1.5s infinite;
  
  @media (max-width: 768px) {
    font-size: 16px;
  }
}

@keyframes pulse-text {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
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

