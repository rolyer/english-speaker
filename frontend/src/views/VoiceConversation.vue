<template>
  <div class="voice-page">
    <!-- Header -->
    <div class="voice-header">
      <div class="header-content">
        <h1 class="page-title">
          <span class="title-icon">🎤</span>
          <span>语音对话</span>
        </h1>
        
        <el-select
          v-model="chatStore.selectedScenario"
          @change="handleScenarioChange"
          class="scenario-select"
          size="large"
        >
          <el-option
            v-for="scenario in chatStore.scenarios"
            :key="scenario.value"
            :label="scenario.label"
            :value="scenario.value"
          >
            <span>{{ scenario.icon }} {{ scenario.label }}</span>
          </el-option>
        </el-select>
      </div>
    </div>
    
    <!-- Messages Container -->
    <div class="messages-container" ref="messagesContainer">
      <!-- Empty State -->
      <div v-if="chatStore.messages.length === 0" class="empty-state">
        <div class="empty-icon animate-float">
          <div class="ai-orb"></div>
          <div class="ai-pulse"></div>
        </div>
        <h2 class="empty-title">开始你的语音对话</h2>
        <p class="empty-subtitle">点击麦克风按钮，用英语说出你的想法</p>
        <div class="empty-tips">
          <div class="tip-item">
            <span class="tip-icon">💡</span>
            <span>清晰的发音会得到更好的评分</span>
          </div>
          <div class="tip-item">
            <span class="tip-icon">🎯</span>
            <span>试着用完整的句子表达</span>
          </div>
        </div>
      </div>
      
      <!-- Messages -->
      <div v-else class="messages-list">
        <!-- AI Status Indicator -->
        <div v-if="chatStore.loading || isAISpeaking" class="ai-status">
          <div class="status-orb" :class="{ 'speaking': isAISpeaking, 'thinking': chatStore.loading }"></div>
          <span class="status-text">
            {{ isAISpeaking ? 'AI正在说话...' : 'AI正在思考...' }}
          </span>
        </div>
        
        <!-- Message Items -->
        <div
          v-for="message in recentMessages"
          :key="message.id"
          class="message-item"
          :class="message.role"
        >
          <div class="message-avatar">
            <span v-if="message.role === 'user'">👤</span>
            <span v-else>🤖</span>
          </div>
          
          <div class="message-content">
            <div class="message-header">
              <span class="message-role">
                {{ message.role === 'user' ? '你' : 'AI老师' }}
              </span>
              <span class="message-time">{{ formatTime(message.created_at) }}</span>
            </div>
            
            <!-- Voice Bubble -->
            <div class="voice-bubble" @click="playMessage(message)">
              <el-icon class="bubble-icon" :class="{ 'playing': isPlayingMessage(message.id) }">
                <VideoPlay v-if="!isPlayingMessage(message.id)" />
                <VideoPause v-else />
              </el-icon>
              
              <div class="sound-waves" :class="{ 'active': isPlayingMessage(message.id) }">
                <span></span>
                <span></span>
                <span></span>
                <span></span>
              </div>
              
              <span class="bubble-duration">{{ getAudioDuration(message) }}s</span>
              
              <!-- Pronunciation Score -->
              <div 
                v-if="message.role === 'user' && message.pronunciation_score != null" 
                class="score-badge"
                :class="getScoreClass(message.pronunciation_score)"
              >
                {{ Math.round(message.pronunciation_score) }}
              </div>
            </div>
            
            <!-- Message Actions -->
            <div class="message-actions">
              <button 
                class="action-btn" 
                @click="toggleText(message)"
                :class="{ 'active': messageStates[message.id]?.showText }"
              >
                <el-icon><Document /></el-icon>
                <span>文本</span>
              </button>
              <button 
                class="action-btn" 
                @click="translateMessage(message)"
                :class="{ 'active': messageStates[message.id]?.translation }"
                :disabled="messageStates[message.id]?.translating"
              >
                <el-icon><Connection /></el-icon>
                <span>翻译</span>
              </button>
            </div>
            
            <!-- Expanded Content -->
            <div v-if="messageStates[message.id]?.showText || messageStates[message.id]?.translation" class="expanded-content">
              <div v-if="messageStates[message.id]?.showText" class="text-content">
                <div class="content-label">原文</div>
                <div class="content-text" v-html="formatMessage(message.content)"></div>
              </div>
              <div v-if="messageStates[message.id]?.translation" class="text-content translation">
                <div class="content-label">翻译</div>
                <div class="content-text" v-html="formatMessage(messageStates[message.id].translation)"></div>
              </div>
            </div>
          </div>
          
          <!-- Hidden Audio Player for AI messages -->
          <AudioPlayer
            v-if="message.role === 'assistant'"
            :ref="el => { if (el) audioPlayerRefs[message.id] = el }"
            :text="message.content"
            :auto-play="false"
            @play="handleAIPlay"
            @pause="handleAIPause"
            @end="handleAIEnd"
            style="display: none;"
          />
        </div>
        
        <!-- Show More Button -->
        <div v-if="chatStore.messages.length > 5" class="show-more">
          <button class="show-more-btn" @click="toggleHistory">
            {{ showFullHistory ? '收起历史' : `查看全部 ${chatStore.messages.length} 条对话` }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Voice Control -->
    <div class="voice-control">
      <div class="control-container">
        <div class="recording-status" v-if="isRecording">
          <div class="recording-indicator">
            <span class="recording-dot"></span>
            <span>正在录音...</span>
          </div>
        </div>
        
        <MediaAudioRecorder
          :language="'en-US'"
          @result="handleVoiceResult"
          @error="handleVoiceError"
          @start="handleVoiceStart"
          @stop="handleVoiceStop"
        />
        
        <div class="control-hint">
          <span>点击麦克风开始录音，再次点击结束</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { useChatStore } from '@/stores/chat'
import { ElMessage } from 'element-plus'
import { VideoPlay, VideoPause, Document, Connection } from '@element-plus/icons-vue'
import MediaAudioRecorder from '@/components/MediaAudioRecorder.vue'
import AudioPlayer from '@/components/AudioPlayer.vue'
import axios from 'axios'

const chatStore = useChatStore()
const messagesContainer = ref(null)
const isRecording = ref(false)
const isAISpeaking = ref(false)
const currentPlayingId = ref(null)
const showFullHistory = ref(false)
const audioPlayerRefs = ref({})
const messageStates = reactive({})

const recentMessages = computed(() => {
  if (showFullHistory.value) {
    return chatStore.messages
  }
  return chatStore.messages.slice(-5)
})

function formatMessage(content) {
  if (!content) return ''
  
  let formatted = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  
  // Markdown formatting
  formatted = formatted.replace(/`([^`]+?)`/g, '<code>$1</code>')
  formatted = formatted.replace(/\*\*([^*]+?)\*\*/g, '<strong>$1</strong>')
  formatted = formatted.replace(/__([^_]+?)__/g, '<strong>$1</strong>')
  formatted = formatted.replace(/\*([^*]+?)\*/g, '<em>$1</em>')
  formatted = formatted.replace(/_([^_]+?)_/g, '<em>$1</em>')
  formatted = formatted.replace(/~~([^~]+?)~~/g, '<del>$1</del>')
  formatted = formatted.replace(/\n/g, '<br>')
  
  return formatted
}

function formatTime(timeString) {
  if (!timeString) return ''
  const date = new Date(timeString)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return date.toLocaleDateString('zh-CN')
}

function getAudioDuration(message) {
  if (!message.content) return 0
  const words = message.content.split(/\s+/).length
  return Math.max(1, Math.min(60, Math.ceil(words * 0.5)))
}

function getScoreClass(score) {
  if (score >= 80) return 'excellent'
  if (score >= 60) return 'good'
  return 'fair'
}

function isPlayingMessage(messageId) {
  return currentPlayingId.value === messageId
}

async function playMessage(message) {
  if (currentPlayingId.value === message.id) {
    stopAudio()
    return
  }
  
  try {
    if (currentPlayingId.value) stopAudio()
    
    currentPlayingId.value = message.id
    
    if (message.role === 'assistant') {
      const audioPlayer = audioPlayerRefs.value[message.id]
      if (audioPlayer && typeof audioPlayer.play === 'function') {
        await audioPlayer.play()
      }
    } else {
      // For user messages, use TTS
      const response = await axios.post('/api/tts/synthesize', {
        text: message.content,
        language: 'en-US'
      }, {
        responseType: 'blob'
      })
      
      const audioBlob = response.data
      const audioUrl = URL.createObjectURL(audioBlob)
      const audio = new Audio(audioUrl)
      
      audio.onended = () => {
        currentPlayingId.value = null
        URL.revokeObjectURL(audioUrl)
      }
      
      await audio.play()
    }
  } catch (error) {
    console.error('播放失败:', error)
    currentPlayingId.value = null
    if (error.name !== 'NotAllowedError') {
      ElMessage.error('音频播放失败')
    }
  }
}

function stopAudio() {
  if (currentPlayingId.value) {
    const audioPlayer = audioPlayerRefs.value[currentPlayingId.value]
    if (audioPlayer && typeof audioPlayer.pause === 'function') {
      audioPlayer.pause()
    }
    currentPlayingId.value = null
    isAISpeaking.value = false
  }
}

function initMessageState(messageId) {
  if (!messageStates[messageId]) {
    messageStates[messageId] = {
      showText: false,
      translation: null,
      translating: false
    }
  }
}

function toggleText(message) {
  initMessageState(message.id)
  messageStates[message.id].showText = !messageStates[message.id].showText
}

async function translateMessage(message) {
  initMessageState(message.id)
  
  if (messageStates[message.id].translation) {
    messageStates[message.id].translation = null
    return
  }
  
  if (messageStates[message.id].translating) return
  
  messageStates[message.id].translating = true
  
  try {
    const response = await axios.post('/api/chat/translate', {
      text: message.content,
      source_lang: 'en',
      target_lang: 'zh'
    })
    messageStates[message.id].translation = response.data.translation
  } catch (error) {
    console.error('翻译失败:', error)
    ElMessage.error('翻译失败，请重试')
  } finally {
    messageStates[message.id].translating = false
  }
}

function toggleHistory() {
  showFullHistory.value = !showFullHistory.value
  nextTick(() => scrollToBottom())
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

async function handleVoiceResult(payload) {
  if (!payload || !payload.audio) {
    ElMessage.error('录音数据无效')
    return
  }
  
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.error('未登录，请先登录')
    return
  }
  
  chatStore.loading = true
  
  try {
    const formData = new FormData()
    formData.append('audio', payload.audio, 'audio.webm')
    formData.append('language', payload.language || 'en')
    if (chatStore.currentConversationId) {
      formData.append('conversation_id', String(chatStore.currentConversationId))
    }
    formData.append('scenario', chatStore.selectedScenario)
    
    const response = await fetch('/api/voice/chat/stream', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    })
    
    if (!response.ok) {
      throw new Error(`请求失败: ${response.status}`)
    }
    
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let fullResponse = ''
    let aiMessageIndex = -1
    
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      buffer += decoder.decode(value, { stream: true })
      const events = buffer.split('\n\n')
      buffer = events.pop() || ''
      
      for (const event of events) {
        const line = event.split('\n').find(l => l.startsWith('data: '))
        if (!line) continue
        
        try {
          const data = JSON.parse(line.slice(6))
          
          if (data.type === 'meta') {
            chatStore.currentConversationId = data.conversation_id
            chatStore.messages.push(data.user_message)
            
            aiMessageIndex = chatStore.messages.length
            chatStore.messages.push({
              id: Date.now(),
              role: 'assistant',
              content: '',
              created_at: new Date().toISOString()
            })
            
            await nextTick()
            scrollToBottom()
            
          } else if (data.type === 'chunk') {
            if (aiMessageIndex >= 0) {
              fullResponse += data.chunk
              chatStore.messages[aiMessageIndex].content = fullResponse
              scrollToBottom()
            }
            
          } else if (data.type === 'done') {
            if (aiMessageIndex >= 0 && data.assistant_message_id) {
              chatStore.messages[aiMessageIndex].id = data.assistant_message_id
            }
            chatStore.currentConversationId = data.conversation_id
            
          } else if (data.type === 'error') {
            throw new Error(data.error || '语音对话失败')
          }
        } catch (e) {
          console.error('解析SSE数据失败:', e)
        }
      }
    }
    
    await nextTick()
    scrollToBottom()
    
  } catch (error) {
    console.error('语音对话失败:', error)
    ElMessage.error('语音对话失败: ' + (error.message || '请重试'))
  } finally {
    chatStore.loading = false
  }
}

function handleVoiceError(error) {
  console.error('语音识别错误:', error)
  ElMessage.error('语音识别失败，请重试')
}

function handleVoiceStart() {
  isRecording.value = true
}

function handleVoiceStop() {
  isRecording.value = false
}

function handleScenarioChange() {
  chatStore.clearMessages()
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
  currentPlayingId.value = null
}

onMounted(async () => {
  // 检查URL参数，如果有conversationId则加载对应的会话
  const route = useRoute()
  const conversationId = route.query.id
  
  if (conversationId) {
    try {
      await chatStore.loadConversation(conversationId)
      await nextTick()
      scrollToBottom()
    } catch (error) {
      console.error('加载会话失败:', error)
      ElMessage.error('加载会话失败')
    }
  }
  
  scrollToBottom()
})
</script>

<style lang="scss" scoped>
.voice-page {
  min-height: calc(100vh - 72px);
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  
  @media (max-width: 768px) {
    min-height: calc(100vh - 64px);
  }
  
  @media (max-width: 860px) {
    // 为移动端底部导航预留空间已在Layout中处理
    min-height: calc(100vh - 64px - 72px);
  }
}

.voice-header {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  padding: var(--space-lg) var(--space-xl);
  
  @media (max-width: 768px) {
    padding: var(--space-md) var(--space-lg);
  }
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-xl);
  min-height: 48px;
}

.page-title {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin: 0;
  line-height: 1;
  flex-shrink: 1;
  min-width: 0;
  
  .title-icon {
    font-size: 1.75rem;
    flex-shrink: 0;
  }
  
  span:not(.title-icon) {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  @media (max-width: 768px) {
    font-size: 1.25rem;
    gap: var(--space-xs);
    
    .title-icon {
      font-size: 1.5rem;
    }
  }
}

.scenario-select {
  width: 180px;
  flex-shrink: 0;
  
  :deep(.el-input__wrapper) {
    padding: var(--space-sm) var(--space-md);
    border-radius: var(--radius-md);
  }
  
  @media (max-width: 768px) {
    width: 140px;
  }
  
  @media (max-width: 480px) {
    width: 120px;
  }
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-2xl) var(--space-xl);
  
  @media (max-width: 768px) {
    padding: var(--space-xl) var(--space-lg);
  }
}

.empty-state {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
  padding: var(--space-3xl) 0;
}

.empty-icon {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto var(--space-2xl);
}

.ai-orb {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: var(--bg-gradient-primary);
  box-shadow: var(--shadow-colored);
}

.ai-pulse {
  position: absolute;
  top: 0;
  left: 0;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: var(--primary);
  opacity: 0.3;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.3;
  }
  50% {
    transform: scale(1.2);
    opacity: 0;
  }
}

.empty-title {
  font-family: var(--font-display);
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--space-md);
}

.empty-subtitle {
  font-size: 1.125rem;
  color: var(--text-secondary);
  margin-bottom: var(--space-2xl);
}

.empty-tips {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  align-items: center;
}

.tip-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-xl);
  background: var(--bg-secondary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  font-size: 0.9375rem;
  color: var(--text-secondary);
  
  .tip-icon {
    font-size: 1.5rem;
  }
}

.messages-list {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

.ai-status {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  justify-content: center;
  padding: var(--space-lg);
  background: var(--bg-secondary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
}

.status-orb {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--primary);
  
  &.thinking {
    animation: pulse 1.5s infinite;
  }
  
  &.speaking {
    animation: pulse 0.8s infinite;
  }
}

.status-text {
  font-weight: 500;
  color: var(--text-secondary);
}

.message-item {
  display: flex;
  gap: var(--space-lg);
  animation: slideUp var(--transition-base) ease-out;
  
  &.assistant {
    flex-direction: row;
  }
  
  &.user {
    flex-direction: row-reverse;
  }
}

.message-avatar {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
  box-shadow: var(--shadow-sm);
  
  .user & {
    background: var(--bg-gradient-primary);
  }
  
  .assistant & {
    background: var(--bg-gradient-secondary);
  }
}

.message-content {
  flex: 1;
  max-width: 70%;
  
  @media (max-width: 768px) {
    max-width: 100%;
  }
}

.message-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-sm);
}

.message-role {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.9375rem;
}

.message-time {
  font-size: 0.8125rem;
  color: var(--text-tertiary);
}

.voice-bubble {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-lg) var(--space-xl);
  background: var(--bg-secondary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  cursor: pointer;
  transition: all var(--transition-base);
  margin-bottom: var(--space-md);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
  }
  
  .user & {
    background: linear-gradient(135deg, rgba(255, 107, 53, 0.1), rgba(255, 133, 87, 0.1));
    border: 2px solid rgba(255, 107, 53, 0.2);
  }
}

.bubble-icon {
  font-size: 1.5rem;
  color: var(--primary);
  transition: transform var(--transition-base);
  
  &.playing {
    animation: pulse 1.5s infinite;
  }
}

.sound-waves {
  display: flex;
  align-items: center;
  gap: 3px;
  height: 24px;
  
  span {
    width: 3px;
    height: 12px;
    background: var(--neutral-300);
    border-radius: 2px;
    transition: all var(--transition-base);
  }
  
  &.active span {
    background: var(--primary);
    animation: wave 0.8s infinite ease-in-out;
    
    &:nth-child(1) { animation-delay: 0s; }
    &:nth-child(2) { animation-delay: 0.1s; }
    &:nth-child(3) { animation-delay: 0.2s; }
    &:nth-child(4) { animation-delay: 0.3s; }
  }
}

@keyframes wave {
  0%, 100% { height: 12px; }
  50% { height: 24px; }
}

.bubble-duration {
  margin-left: auto;
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.score-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.75rem;
  color: var(--text-inverse);
  box-shadow: var(--shadow-md);
  
  &.excellent {
    background: var(--success);
  }
  
  &.good {
    background: var(--accent);
  }
  
  &.fair {
    background: var(--neutral-400);
  }
}

.message-actions {
  display: flex;
  gap: var(--space-sm);
  margin-bottom: var(--space-md);
}

.action-btn {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-sm) var(--space-md);
  border: 1px solid var(--border-color);
  background: transparent;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: var(--font-body);
  
  &:hover:not(:disabled) {
    border-color: var(--primary);
    color: var(--primary);
    background: rgba(255, 107, 53, 0.05);
  }
  
  &.active {
    border-color: var(--primary);
    color: var(--primary);
    background: rgba(255, 107, 53, 0.1);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.expanded-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  animation: slideDown var(--transition-base) ease-out;
}

.text-content {
  padding: var(--space-lg);
  background: var(--bg-tertiary);
  border-radius: var(--radius-lg);
  border-left: 3px solid var(--primary);
  
  &.translation {
    border-left-color: var(--secondary);
  }
}

.content-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--space-xs);
}

.content-text {
  color: var(--text-primary);
  line-height: 1.6;
  word-wrap: break-word;
  
  :deep(strong) {
    font-weight: 600;
    color: var(--text-primary);
  }
  
  :deep(em) {
    font-style: italic;
  }
  
  :deep(del) {
    text-decoration: line-through;
    opacity: 0.7;
  }
  
  :deep(code) {
    background: rgba(0, 0, 0, 0.05);
    padding: 2px 6px;
    border-radius: var(--radius-sm);
    font-family: var(--font-mono);
    font-size: 0.9em;
  }
}

.show-more {
  text-align: center;
  padding: var(--space-xl) 0;
}

.show-more-btn {
  padding: var(--space-md) var(--space-xl);
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  color: var(--text-secondary);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
  font-family: var(--font-body);
  
  &:hover {
    border-color: var(--primary);
    color: var(--primary);
    box-shadow: var(--shadow-sm);
  }
}

.voice-control {
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
  padding: var(--space-xl);
  
  @media (max-width: 768px) {
    padding: var(--space-lg);
  }
}

.control-container {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
}

.recording-status {
  margin-bottom: var(--space-lg);
}

.recording-indicator {
  display: inline-flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-xl);
  background: rgba(239, 68, 68, 0.1);
  border-radius: var(--radius-full);
  color: var(--error);
  font-weight: 600;
}

.recording-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--error);
  animation: pulse 1s infinite;
}

.control-hint {
  margin-top: var(--space-lg);
  color: var(--text-tertiary);
  font-size: 0.875rem;
}
</style>

