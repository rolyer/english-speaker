<template>
  <div class="conversation-page">
    <div class="conversation-header">
      <h2>💬 英语对话练习</h2>
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
    
    <div class="conversation-container" ref="messagesContainer">
      <div v-if="chatStore.messages.length === 0" class="empty-state">
        <p>👋 开始和AI老师对话吧！</p>
        <p class="hint">选择上方场景，然后输入你的问题</p>
      </div>
      
      <div
        v-for="message in chatStore.messages"
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
            <div class="message-actions">
              <AudioPlayer
                v-if="message.role === 'assistant'"
                :text="message.content"
                :auto-play="false"
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
    
    <div class="conversation-input">
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
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useChatStore } from '@/stores/chat'
import { useUserStore } from '@/stores/user'
import { isMobile } from '@/utils/device'
import { ElMessage } from 'element-plus'
import AudioPlayer from '@/components/AudioPlayer.vue'

const router = useRouter()
const route = useRoute()
const chatStore = useChatStore()
const userStore = useUserStore()
const inputMessage = ref('')
const inputRef = ref(null)
const messagesContainer = ref(null)
const mobile = computed(() => isMobile())

function formatMessage(content) {
  // 简单的Markdown渲染（换行）
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

async function handleSend() {
  if (!inputMessage.value.trim() || chatStore.loading) return
  
  // 检查是否已登录
  if (!userStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
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
  
  // 移动端：输入框失焦后重新聚焦
  if (mobile.value) {
    await nextTick()
    inputRef.value?.focus()
  }
}

function handleScenarioChange() {
  chatStore.clearMessages()
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 监听键盘事件
function handleKeyPress(event) {
  // 移动端：Enter键发送（不换行）
  if (mobile.value && event.key === 'Enter' && !event.shiftKey && !event.ctrlKey && !event.metaKey) {
    event.preventDefault()
    handleSend()
  }
}

onMounted(async () => {
  document.addEventListener('keydown', handleKeyPress)
  
  // 检查URL参数，如果有conversation_id则加载历史会话
  const conversationId = route.query.id
  if (conversationId) {
    try {
      await chatStore.loadConversation(parseInt(conversationId))
      ElMessage.success('已加载历史会话')
      await nextTick()
      scrollToBottom()
    } catch (error) {
      console.error('加载历史会话失败:', error)
      ElMessage.error('加载历史会话失败')
      // 清空消息，开始新会话
      chatStore.clearMessages()
    }
  } else if (!chatStore.currentConversationId) {
    // 只有在没有当前会话ID时才清空消息（避免清除从其他页面带来的会话）
    chatStore.clearMessages()
  }
  
  scrollToBottom()
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyPress)
})
</script>

<style lang="scss" scoped>
.conversation-page {
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

.conversation-header {
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
  margin-bottom: 4px;
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
    animation: typing 1.4s infinite;
    
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

.conversation-input {
  padding: 16px 20px;
  background: white;
  border-top: 1px solid var(--border-color);
  
  @media (max-width: 768px) {
    padding: 12px;
  }
}

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
</style>
