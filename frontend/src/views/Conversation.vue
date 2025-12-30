<template>
  <div class="conversation-page">
    <!-- Header -->
    <div class="conversation-header">
      <div class="header-content">
        <h1 class="page-title">
          <span class="title-icon">💬</span>
          <span>文本对话</span>
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
        <h2 class="empty-title">开始文本对话</h2>
        <p class="empty-subtitle">在下方输入框输入你的问题，AI老师会帮助你练习英语</p>
      </div>
      
      <!-- Messages -->
      <div v-else class="messages-list">
        <div
          v-for="message in chatStore.messages"
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
            
            <div class="message-bubble">
              <div class="message-text" v-html="formatMessage(message.content)"></div>
              
              <div v-if="message.role === 'assistant'" class="message-actions">
                <AudioPlayer
                  :text="message.content"
                  :auto-play="false"
                />
              </div>
            </div>
          </div>
        </div>
        
        <!-- Typing Indicator -->
        <div v-if="chatStore.loading" class="typing-indicator">
          <div class="message-avatar">
            <span>🤖</span>
          </div>
          <div class="typing-bubble">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Input Area -->
    <div class="input-area">
      <div class="input-container">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="3"
          placeholder="输入你的消息..."
          :disabled="chatStore.loading"
          @keydown.enter.exact="handleEnterKey"
          class="message-input"
        />
        
        <el-button
          type="primary"
          :loading="chatStore.loading"
          :disabled="!inputMessage.trim()"
          @click="handleSend"
          class="send-button"
        >
          <span v-if="!chatStore.loading">发送</span>
          <span v-else>发送中...</span>
        </el-button>
      </div>
      
      <div class="input-hint">
        按 Enter 发送，Shift + Enter 换行
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useChatStore } from '@/stores/chat'
import { ElMessage } from 'element-plus'
import AudioPlayer from '@/components/AudioPlayer.vue'

const chatStore = useChatStore()
const inputMessage = ref('')
const messagesContainer = ref(null)

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

function handleEnterKey(event) {
  if (event.shiftKey) {
    return
  }
  event.preventDefault()
  handleSend()
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
    const errorMessage = error.message || '发送消息失败，请重试'
    if (errorMessage.includes('登录') || errorMessage.includes('未授权')) {
      ElMessage.error(errorMessage)
    } else {
      ElMessage.error('发送消息失败，请重试')
      console.error('发送消息错误:', error)
    }
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
  ElMessage.success(`已切换到场景：${chatStore.selectedScenario}`)
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
.conversation-page {
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

.conversation-header {
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
}

.messages-list {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
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

.message-bubble {
  background: var(--bg-secondary);
  padding: var(--space-lg) var(--space-xl);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  
  .user & {
    background: linear-gradient(135deg, rgba(255, 107, 53, 0.1), rgba(255, 133, 87, 0.1));
    border: 2px solid rgba(255, 107, 53, 0.2);
  }
}

.message-text {
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

.message-actions {
  margin-top: var(--space-md);
  padding-top: var(--space-md);
  border-top: 1px solid var(--border-color-light);
}

.typing-indicator {
  display: flex;
  gap: var(--space-lg);
  animation: slideUp var(--transition-base) ease-out;
}

.typing-bubble {
  background: var(--bg-secondary);
  padding: var(--space-lg) var(--space-xl);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  
  span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--text-tertiary);
    animation: typing 1.4s infinite;
    
    &:nth-child(1) {
      animation-delay: 0s;
    }
    
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
    transform: translateY(-8px);
    opacity: 1;
  }
}

.input-area {
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
  padding: var(--space-xl);
  
  @media (max-width: 768px) {
    padding: var(--space-lg);
  }
}

.input-container {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  gap: var(--space-md);
  align-items: flex-end;
  
  @media (max-width: 768px) {
    flex-direction: column;
    align-items: stretch;
  }
}

.message-input {
  flex: 1;
  
  :deep(.el-textarea__inner) {
    border-radius: var(--radius-lg);
    border: 2px solid var(--border-color);
    font-size: 1rem;
    line-height: 1.6;
    resize: none;
    font-family: var(--font-body);
    transition: all var(--transition-base);
    
    &:focus {
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
    }
    
    &::placeholder {
      color: var(--text-tertiary);
    }
  }
}

.send-button {
  height: 56px;
  padding: 0 var(--space-3xl);
  font-size: 1rem;
  font-weight: 600;
  border-radius: var(--radius-lg);
  background: var(--bg-gradient-primary);
  border: none;
  box-shadow: var(--shadow-colored);
  transition: all var(--transition-base);
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: var(--shadow-xl);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  @media (max-width: 768px) {
    width: 100%;
  }
}

.input-hint {
  max-width: 900px;
  margin: var(--space-md) auto 0;
  text-align: center;
  color: var(--text-tertiary);
  font-size: 0.875rem;
  
  @media (max-width: 768px) {
    display: none;
  }
}
</style>
