<template>
  <div class="voice-conversation-page">
    <div class="voice-header">
      <h2>🎤 语音对话模式</h2>
      <el-switch
        v-model="voiceMode"
        active-text="语音模式"
        inactive-text="文本模式"
        @change="handleModeChange"
        size="small"
      />
    </div>
    
    <div class="conversation-container" ref="messagesContainer">
      <div v-if="chatStore.messages.length === 0" class="empty-state">
        <p>🎙️ 点击下方按钮开始语音对话</p>
        <p class="hint">说出你的问题，AI老师会帮助你练习英语</p>
      </div>
      
      <div
        v-for="(message, index) in chatStore.messages"
        :key="message.id"
        :class="['message', message.role]"
      >
        <div class="message-content">
          <div class="message-avatar">
            <span v-if="message.role === 'user'">👤</span>
            <span v-else>🤖</span>
          </div>
          <div class="message-bubble">
            <div class="message-text" v-html="formatMessage(message.content)"></div>
            
            <div v-if="message.role === 'user' && message.pronunciation_score !== null" class="pronunciation-result">
              <PronunciationScore
                :score="message.pronunciation_score"
                :feedback="message.pronunciation_feedback || []"
              />
            </div>
            
            <div class="message-actions">
              <AudioPlayer
                v-if="message.role === 'assistant'"
                :text="message.content"
                :auto-play="voiceMode && isLatestAssistantMessage(index)"
              />
              <div class="message-time">{{ formatTime(message.created_at) }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="chatStore.loading" class="message assistant">
        <div class="message-content">
          <div class="message-avatar">🤖</div>
          <div class="message-bubble">
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
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
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="mobile ? 3 : 2"
          placeholder="输入你的问题..."
          :disabled="chatStore.loading"
          @keyup.ctrl.enter="handleSend"
          @keyup.meta.enter="handleSend"
          ref="inputRef"
          class="input-textarea"
        />
        <div class="input-actions">
          <el-button
            type="primary"
            :loading="chatStore.loading"
            @click="handleSend"
            :disabled="!inputMessage.trim()"
            size="large"
            class="send-button"
          >
            发送
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import { isMobile } from '@/utils/device'
import { ElMessage } from 'element-plus'
import AudioRecorder from '@/components/AudioRecorder.vue'
import AudioPlayer from '@/components/AudioPlayer.vue'
import PronunciationScore from '@/components/PronunciationScore.vue'
import api from '@/services/api'

const chatStore = useChatStore()
const inputMessage = ref('')
const inputRef = ref(null)
const messagesContainer = ref(null)
const voiceMode = ref(false)
const mobile = computed(() => isMobile())
const isRecording = ref(false)

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

async function handleSend() {
  if (!inputMessage.value.trim() || chatStore.loading) return
  
  const message = inputMessage.value.trim()
  inputMessage.value = ''
  
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

// 判断是否是最新的AI消息
function isLatestAssistantMessage(index) {
  // 从当前索引往后查找，如果没有其他assistant消息，则这是最新的
  for (let i = index + 1; i < chatStore.messages.length; i++) {
    if (chatStore.messages[i].role === 'assistant') {
      return false
    }
  }
  return true
}

onMounted(() => {
  scrollToBottom()
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
    height: calc(100vh - 60px);
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
}

.conversation-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  scroll-behavior: smooth;
  
  @media (max-width: 768px) {
    padding: 12px;
  }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-light);
  
  p {
    margin: 10px 0;
    font-size: 1.1rem;
  }
  
  .hint {
    font-size: 0.9rem;
    opacity: 0.7;
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
  .input-textarea {
    margin-bottom: 12px;
    
    :deep(.el-textarea__inner) {
      resize: none;
      font-size: 14px;
      line-height: 1.6;
    }
  }
  
  .input-actions {
    display: flex;
    justify-content: flex-end;
  }
  
  .send-button {
    min-width: 80px;
    
    @media (max-width: 768px) {
      width: 100%;
      min-height: 44px;
    }
  }
}
</style>

