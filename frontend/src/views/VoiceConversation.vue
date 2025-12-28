<template>
  <div class="voice-conversation-page">
    <div class="voice-header">
      <h2>🎤 语音对话</h2>
      <el-select
        v-model="chatStore.selectedScenario"
        @change="handleScenarioChange"
        size="small"
        class="scenario-select"
      >
        <el-option
          v-for="scenario in chatStore.scenarios"
          :key="scenario.value"
          :label="scenario.icon + ' ' + scenario.label"
          :value="scenario.value"
        />
      </el-select>
    </div>
    
    <!-- 语音对话主界面 -->
    <div class="voice-main-container" ref="messagesContainer">
      <!-- 空状态 -->
      <div v-if="chatStore.messages.length === 0" class="voice-empty-state">
        <div class="voice-assistant-avatar">
          <div class="avatar-circle">
            <span class="avatar-icon">🤖</span>
          </div>
          <div class="avatar-pulse"></div>
        </div>
        <h3>AI 英语老师</h3>
        <p>点击下方麦克风按钮开始对话</p>
      </div>
      
      <!-- 对话进行中 -->
      <div v-else class="voice-conversation-active">
        <!-- AI 头像和状态 -->
        <div class="ai-avatar-section">
          <div class="ai-avatar" :class="{ 'speaking': isAISpeaking }">
            <span class="avatar-icon">🤖</span>
            <div v-if="isAISpeaking" class="sound-wave">
              <span></span>
              <span></span>
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
          <div v-if="chatStore.loading && isWaitingForFirstResponse" class="ai-status">
            AI 正在思考...
          </div>
          <div v-else-if="isAISpeaking" class="ai-status">
            AI 正在说话...
          </div>
        </div>
        
        <!-- 最近的对话内容（简化显示） -->
        <div class="recent-messages">
          <div
            v-for="message in recentMessages"
            :key="message.id"
            :class="['voice-message', message.role]"
          >
            <div class="voice-message-header">
              <span class="speaker-label">
                {{ message.role === 'user' ? '你' : 'AI老师' }}
              </span>
              <span class="message-time">{{ formatTime(message.created_at) }}</span>
            </div>
            
            <!-- 用户消息：显示发音评分 -->
            <div v-if="message.role === 'user'" class="user-voice-content">
              <PronunciationScore
                v-if="message.pronunciation_score !== null && message.pronunciation_score !== undefined"
                :score="message.pronunciation_score"
                :feedback="message.pronunciation_feedback || []"
              />
              <div class="transcription">{{ message.content }}</div>
            </div>
            
            <!-- AI 消息：显示播放按钮 -->
            <div v-else class="ai-voice-content">
              <AudioPlayer
                :ref="el => { if (el) audioPlayerRefs[message.id] = el }"
                :text="message.content"
                :auto-play="false"
                @play="handleAIPlay"
                @pause="handleAIPause"
                @end="handleAIEnd"
              />
              <div class="transcription" v-if="showTranscription">{{ message.content }}</div>
            </div>
          </div>
        </div>
        
        <!-- 查看完整对话历史按钮 -->
        <div v-if="chatStore.messages.length > 3" class="view-history">
          <el-button text @click="toggleHistoryView">
            {{ showFullHistory ? '收起历史' : `查看全部 ${chatStore.messages.length} 条对话` }}
          </el-button>
        </div>
      </div>
    </div>
    
    <div class="voice-controls">
      <div v-if="voiceMode" class="voice-input-section">
        <AudioRecorder
          :language="'en-US'"
          :continuous="false"
          @result="handleVoiceResult"
          @error="handleVoiceError"
          @start="handleVoiceStart"
          @stop="handleVoiceStop"
        />
      </div>
      
      <div v-else class="text-input-section">
        <div class="input-wrapper">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="mobile ? 3 : 2"
            placeholder="输入你的问题，按回车发送..."
            :disabled="chatStore.loading"
            @keydown.enter.exact="handleEnterKey"
            ref="inputRef"
            class="input-textarea"
          />
          <el-button
            type="primary"
            :loading="chatStore.loading"
            @click="handleSend"
            :disabled="!inputMessage.trim()"
            :icon="mobile ? 'Position' : ''"
            circle
            class="send-button"
          >
            <el-icon v-if="!mobile"><Position /></el-icon>
          </el-button>
        </div>
        <div v-if="!mobile" class="input-hint">
          按 Enter 发送，Shift + Enter 换行
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import { isMobile } from '@/utils/device'
import { ElMessage } from 'element-plus'
import { Position } from '@element-plus/icons-vue'
import AudioRecorder from '@/components/AudioRecorder.vue'
import AudioPlayer from '@/components/AudioPlayer.vue'
import PronunciationScore from '@/components/PronunciationScore.vue'
import api from '@/services/api'

const chatStore = useChatStore()
const inputMessage = ref('')
const inputRef = ref(null)
const messagesContainer = ref(null)
const voiceMode = ref(true) // 语音对话页面默认开启语音模式
const mobile = computed(() => isMobile())
const isRecording = ref(false)
const lastPlayedMessageId = ref(null) // 记录最后播放的消息ID
const enableAutoPlay = ref(false) // 是否启用自动播放（只有在用户发送消息后才启用）
const audioPlayerRefs = ref({}) // 存储所有 AudioPlayer 组件的引用
const isAISpeaking = ref(false) // AI 是否正在说话
const showTranscription = ref(false) // 是否显示文本转录
const showFullHistory = ref(false) // 是否显示完整历史

// 判断是否在等待第一个响应（还没有收到任何内容）
const isWaitingForFirstResponse = computed(() => {
  if (!chatStore.loading) return false
  
  // 如果消息列表为空，或者最后一条消息是用户消息，说明正在等待 AI 响应
  if (chatStore.messages.length === 0) return true
  
  const lastMessage = chatStore.messages[chatStore.messages.length - 1]
  return lastMessage.role === 'user'
})

// 只显示最近的几条消息
const recentMessages = computed(() => {
  if (showFullHistory.value) {
    return chatStore.messages
  }
  return chatStore.messages.slice(-3) // 只显示最近3条
})

function formatMessage(content) {
  return content.replace(/\n/g, '<br>')
}

function formatTime(timeString) {
  if (!timeString) return ''
  const date = new Date(timeString)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) {
    return '刚刚'
  } else if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}

async function handleVoiceResult(text) {
  if (!text.trim()) return
  
  // 用户发送消息后，启用自动播放
  enableAutoPlay.value = true
  
  try {
    // 发送语音识别的文本
    await chatStore.sendMessageStream(
      text,
      chatStore.currentConversationId,
      () => {
        scrollToBottom()
      }
    )
    await nextTick()
    scrollToBottom()
  } catch (error) {
    ElMessage.error('发送消息失败，请重试')
  }
}

async function handleVoiceError(error) {
  console.error('语音识别错误:', error)
  ElMessage.error('语音识别失败，请重试')
}

function handleVoiceStart() {
  isRecording.value = true
}

function handleVoiceStop() {
  isRecording.value = false
}

function handleModeChange() {
  if (!voiceMode.value) {
    // 切换到文本模式
    nextTick(() => {
      inputRef.value?.focus()
    })
  }
}

// 处理回车键
function handleEnterKey(event) {
  // Shift + Enter 换行
  if (event.shiftKey) {
    return // 允许默认换行行为
  }
  
  // 单独按 Enter 发送消息
  event.preventDefault()
  handleSend()
}

async function handleSend() {
  if (!inputMessage.value.trim() || chatStore.loading) return
  
  const message = inputMessage.value.trim()
  inputMessage.value = ''
  
  // 用户发送消息后，启用自动播放
  enableAutoPlay.value = true
  
  try {
    await chatStore.sendMessageStream(
      message,
      chatStore.currentConversationId,
      () => {
        scrollToBottom()
      }
    )
    await nextTick()
    scrollToBottom()
  } catch (error) {
    // 显示更详细的错误信息
    const errorMessage = error.message || '发送消息失败，请重试'
    if (errorMessage.includes('登录') || errorMessage.includes('未授权')) {
      ElMessage.error(errorMessage)
    } else {
      ElMessage.error('发送消息失败，请重试')
      console.error('发送消息错误:', error)
    }
  }
  
  if (mobile.value) {
    await nextTick()
    inputRef.value?.focus()
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

function handleScenarioChange() {
  chatStore.clearMessages()
  lastPlayedMessageId.value = null
  ElMessage.success(`已切换到场景：${chatStore.selectedScenario}`)
}

function handleAIPlay() {
  isAISpeaking.value = true
}

function handleAIPause() {
  isAISpeaking.value = false
}

function handleAIEnd() {
  isAISpeaking.value = false
}

function toggleHistoryView() {
  showFullHistory.value = !showFullHistory.value
  nextTick(() => {
    scrollToBottom()
  })
}

// 判断是否是最新的AI消息
function isLatestAssistantMessage(index) {
  // 从当前索引往后查找，如果没有其他assistant消息，则这是最新的
  for (let i = index + 1; i < chatStore.messages.length; i++) {
    if (chatStore.messages[i].role === 'assistant') {
      return false
    }
  }
  // 同时检查消息内容不为空（避免在流式响应开始时就触发）
  const message = chatStore.messages[index]
  const isLatest = message && message.content && message.content.trim().length > 0
  
  if (isLatest) {
    console.log('[VoiceConversation] 最新AI消息:', {
      index,
      contentLength: message.content.length,
      voiceMode: voiceMode.value,
      autoPlay: voiceMode.value && isLatest
    })
  }
  
  return isLatest
}

// 监听消息变化，当新的 assistant 消息完成时自动播放
let autoPlayTimer = null
watch(() => chatStore.messages, (newMessages) => {
  console.log('[VoiceConversation] watch 触发:', {
    enableAutoPlay: enableAutoPlay.value,
    voiceMode: voiceMode.value,
    loading: chatStore.loading,
    messagesCount: newMessages.length
  })
  
  // 只有在启用自动播放和语音模式开启时才处理（不检查 loading，因为流式响应过程中 loading 可能是 true）
  if (!enableAutoPlay.value || !voiceMode.value) {
    console.log('[VoiceConversation] 跳过自动播放检查')
    return
  }
  
  // 清除之前的定时器
  if (autoPlayTimer) {
    clearTimeout(autoPlayTimer)
  }
  
  // 找到最后一条 assistant 消息
  const lastAssistantMessage = [...newMessages].reverse().find(msg => msg.role === 'assistant')
  
  if (lastAssistantMessage && lastAssistantMessage.content && lastAssistantMessage.content.trim().length > 0) {
    // 如果这条消息还没有播放过
    if (lastAssistantMessage.id !== lastPlayedMessageId.value) {
      console.log('[VoiceConversation] 检测到新的 assistant 消息，准备自动播放, 消息ID:', lastAssistantMessage.id)
      
      // 设置定时器，等待流式响应完成
      autoPlayTimer = setTimeout(async () => {
        // 再次检查，确保不是在加载中
        if (!chatStore.loading && voiceMode.value && enableAutoPlay.value && lastAssistantMessage.id !== lastPlayedMessageId.value) {
          console.log('[VoiceConversation] ✅ 开始自动播放音频，消息ID:', lastAssistantMessage.id)
          lastPlayedMessageId.value = lastAssistantMessage.id
          
          // 等待 DOM 更新，确保 AudioPlayer 组件已渲染
          await nextTick()
          
          // 获取对应的 AudioPlayer 组件引用并调用 play 方法
          const audioPlayer = audioPlayerRefs.value[lastAssistantMessage.id]
          if (audioPlayer && typeof audioPlayer.play === 'function') {
            try {
              await audioPlayer.play()
              console.log('[VoiceConversation] ✅ 通过 AudioPlayer 组件播放成功')
            } catch (error) {
              console.error('[VoiceConversation] ❌ AudioPlayer 播放失败:', error)
              // 如果是浏览器自动播放策略导致的错误，不显示错误消息
              if (error.name !== 'NotAllowedError') {
                ElMessage.error('音频播放失败')
              }
            }
          } else {
            console.error('[VoiceConversation] ❌ 找不到 AudioPlayer 组件引用:', lastAssistantMessage.id)
          }
        } else {
          console.log('[VoiceConversation] ❌ 取消自动播放:', {
            loading: chatStore.loading,
            voiceMode: voiceMode.value,
            enableAutoPlay: enableAutoPlay.value,
            alreadyPlayed: lastAssistantMessage.id === lastPlayedMessageId.value
          })
        }
      }, 1500) // 等待1500ms确保流式响应完成
    }
  }
}, { deep: true })

onMounted(async () => {
  // 页面加载时，不启用自动播放（避免浏览器自动播放策略限制）
  enableAutoPlay.value = false
  
  // 如果没有当前会话，尝试加载最新的对话
  if (!chatStore.currentConversationId) {
    try {
      const latestConversation = await chatStore.loadLatestConversation()
      if (latestConversation) {
        console.log('已自动加载最新对话')
        // 记录已加载的消息ID，避免自动播放历史消息
        const lastAssistantMessage = [...chatStore.messages].reverse().find(msg => msg.role === 'assistant')
        if (lastAssistantMessage) {
          lastPlayedMessageId.value = lastAssistantMessage.id
        }
        await nextTick()
        scrollToBottom()
      } else {
        // 没有历史对话，保持空白状态
        console.log('没有历史对话记录')
      }
    } catch (error) {
      console.error('加载最新对话失败:', error)
      // 加载失败，保持空白状态
    }
  } else {
    // 如果已经有当前会话（从其他页面导航过来），记录最后的消息ID
    const lastAssistantMessage = [...chatStore.messages].reverse().find(msg => msg.role === 'assistant')
    if (lastAssistantMessage) {
      lastPlayedMessageId.value = lastAssistantMessage.id
    }
  }
  
  scrollToBottom()
})

onUnmounted(() => {
  if (autoPlayTimer) {
    clearTimeout(autoPlayTimer)
  }
})
</script>

<style lang="scss" scoped>
.voice-conversation-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 64px);
  max-width: 1200px;
  margin: 0 auto;
  background: var(--bg-light);
  
  @media (max-width: 768px) {
    height: calc(100vh - 56px); // 移动端顶部导航高度
  }
}

.voice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: white;
  border-bottom: 1px solid var(--border-color);
  
  h2 {
    margin: 0;
    color: var(--primary-color);
    font-size: 1.5rem;
  }
  
  .scenario-select {
    width: 150px;
    
    @media (max-width: 768px) {
      width: 120px;
    }
  }
}

// 语音对话主容器
.voice-main-container {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  scroll-behavior: smooth;
  
  @media (max-width: 768px) {
    padding: 20px 12px;
  }
}

// 空状态 - 语音助手风格
.voice-empty-state {
  text-align: center;
  animation: fadeIn 0.5s ease-out;
  
  .voice-assistant-avatar {
    position: relative;
    width: 120px;
    height: 120px;
    margin: 0 auto 30px;
    
    .avatar-circle {
      width: 120px;
      height: 120px;
      border-radius: 50%;
      background: linear-gradient(135deg, var(--primary-color), #667eea);
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
      position: relative;
      z-index: 2;
      
      .avatar-icon {
        font-size: 60px;
      }
    }
    
    .avatar-pulse {
      position: absolute;
      top: 0;
      left: 0;
      width: 120px;
      height: 120px;
      border-radius: 50%;
      background: var(--primary-color);
      opacity: 0.3;
      animation: pulse 2s infinite;
      z-index: 1;
    }
  }
  
  h3 {
    font-size: 1.5rem;
    color: var(--text-color);
    margin: 0 0 10px 0;
  }
  
  p {
    color: var(--text-light);
    font-size: 1rem;
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.3;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.1;
  }
}

// 对话进行中
.voice-conversation-active {
  width: 100%;
  max-width: 600px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

// AI 头像区域
.ai-avatar-section {
  text-align: center;
  margin-bottom: 40px;
  
  .ai-avatar {
    position: relative;
    width: 100px;
    height: 100px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--primary-color), #667eea);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 16px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    
    .avatar-icon {
      font-size: 50px;
    }
    
    &.speaking {
      animation: avatarPulse 1.5s infinite;
      box-shadow: 0 4px 24px rgba(255, 107, 157, 0.4);
    }
    
    .sound-wave {
      position: absolute;
      bottom: -30px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      gap: 4px;
      
      span {
        width: 3px;
        height: 20px;
        background: var(--primary-color);
        border-radius: 2px;
        animation: soundWave 1s infinite ease-in-out;
        
        &:nth-child(1) { animation-delay: 0s; }
        &:nth-child(2) { animation-delay: 0.1s; }
        &:nth-child(3) { animation-delay: 0.2s; }
        &:nth-child(4) { animation-delay: 0.3s; }
        &:nth-child(5) { animation-delay: 0.4s; }
      }
    }
  }
  
  .ai-status {
    color: var(--primary-color);
    font-size: 0.9rem;
    font-weight: 500;
    animation: fadeIn 0.3s ease-out;
  }
}

@keyframes avatarPulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

@keyframes soundWave {
  0%, 100% {
    height: 10px;
  }
  50% {
    height: 25px;
  }
}

// 最近的消息
.recent-messages {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.voice-message {
  background: white;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  animation: slideUp 0.3s ease-out;
  
  &.user {
    border-left: 4px solid var(--primary-color);
  }
  
  &.assistant {
    border-left: 4px solid #667eea;
  }
  
  .voice-message-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    
    .speaker-label {
      font-weight: 600;
      color: var(--text-color);
      font-size: 0.95rem;
    }
    
    .message-time {
      font-size: 0.75rem;
      color: var(--text-light);
    }
  }
  
  .user-voice-content,
  .ai-voice-content {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  .transcription {
    font-size: 0.9rem;
    color: var(--text-light);
    line-height: 1.6;
    padding: 8px 12px;
    background: var(--bg-light);
    border-radius: 8px;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 查看历史按钮
.view-history {
  margin-top: 20px;
  text-align: center;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.message {
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease-out;
  
  &.user {
    .message-content {
      flex-direction: row-reverse;
    }
    
    .message-bubble {
      background: var(--primary-color);
      color: white;
      border-radius: 18px 18px 4px 18px;
    }
  }
  
  &.assistant {
    .message-bubble {
      background: white;
      color: var(--text-color);
      border-radius: 18px 18px 18px 4px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
  }
}

.message-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  max-width: 70%;
  margin-left: auto;
  
  @media (max-width: 768px) {
    max-width: 85%;
  }
  
  .user & {
    margin-left: 0;
    margin-right: auto;
  }
}

.message-avatar {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
  
  @media (max-width: 768px) {
    width: 36px;
    height: 36px;
    font-size: 20px;
  }
}

.message-bubble {
  padding: 12px 16px;
  word-wrap: break-word;
  flex: 1;
  
  @media (max-width: 768px) {
    padding: 10px 14px;
    font-size: 14px;
  }
}

.message-text {
  line-height: 1.6;
  margin-bottom: 8px;
}

.pronunciation-result {
  margin-top: 12px;
  margin-bottom: 8px;
}

.message-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.6;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
  
  span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--text-light);
    animation: typing 1.5s infinite;
    
    &:nth-child(2) {
      animation-delay: 0.2s;
    }
    
    &:nth-child(3) {
      animation-delay: 0.4s;
    }
  }
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.5;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

.voice-controls {
  padding: 16px 20px;
  background: white;
  border-top: 1px solid var(--border-color);
  
  @media (max-width: 768px) {
    padding: 12px;
  }
}

.voice-input-section {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.text-input-section {
  .input-wrapper {
    position: relative;
  }
  
  .input-textarea {
    width: 100%;
    
    :deep(.el-textarea__inner) {
      resize: none;
      font-size: 14px;
      line-height: 1.6;
      padding-right: 52px; // 所有设备都为发送按钮留出空间
      
      @media (max-width: 768px) {
        font-size: 16px; // 移动端稍大一些，防止自动缩放
      }
    }
  }
  
  .send-button {
    position: absolute;
    right: 8px;
    bottom: 8px;
    width: 40px;
    height: 40px;
    font-size: 20px;
    transition: transform 0.2s ease;
    
    &:hover {
      transform: scale(1.05);
    }
    
    &:active {
      transform: scale(0.95);
    }
  }
  
  .input-hint {
    margin-top: 8px;
    font-size: 0.75rem;
    color: var(--text-light);
    text-align: right;
    opacity: 0.7;
  }
}
</style>

