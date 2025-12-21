import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useChatStore = defineStore('chat', () => {
  const conversations = ref([])
  const currentConversationId = ref(null)
  const messages = ref([])
  const loading = ref(false)
  const selectedScenario = ref('general')

  const scenarios = [
    { value: 'general', label: '日常对话', icon: '💬' },
    { value: 'school', label: '学校生活', icon: '🏫' },
    { value: 'home', label: '家庭生活', icon: '🏠' },
    { value: 'shopping', label: '购物', icon: '🛒' },
    { value: 'travel', label: '旅行', icon: '✈️' }
  ]

  async function fetchConversations() {
    try {
      const response = await api.get('/chat/conversations')
      conversations.value = response
      return response
    } catch (error) {
      console.error('获取对话列表失败:', error)
      throw error
    }
  }

  async function sendMessage(message, conversationId = null) {
    loading.value = true
    try {
      const response = await api.post('/chat/', {
        message,
        conversation_id: conversationId,
        scenario: selectedScenario.value
      })
      
      if (!conversationId) {
        currentConversationId.value = response.conversation_id
      }
      
      // 添加消息到列表
      messages.value.push({
        id: Date.now(),
        role: 'user',
        content: message,
        created_at: new Date().toISOString()
      })
      
      messages.value.push({
        id: response.message_id,
        role: 'assistant',
        content: response.response,
        created_at: new Date().toISOString()
      })
      
      return response
    } catch (error) {
      console.error('发送消息失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function sendMessageStream(message, conversationId = null, onChunk) {
    loading.value = true
    let fullResponse = ''
    let tempMessageId = Date.now()
    
    // 添加用户消息
    messages.value.push({
      id: tempMessageId++,
      role: 'user',
      content: message,
      created_at: new Date().toISOString()
    })
    
    // 添加空的AI消息用于流式更新
    const aiMessageIndex = messages.value.length
    messages.value.push({
      id: tempMessageId++,
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString()
    })
    
    try {
      // 检查token是否存在
      const token = localStorage.getItem('token')
      if (!token) {
        throw new Error('未登录，请先登录')
      }
      
      // 使用 /api 前缀，Vite 代理会将其转发到后端
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
          scenario: selectedScenario.value
        })
      })
      
      if (!response.ok) {
        // 处理401未授权错误
        if (response.status === 401) {
          localStorage.removeItem('token')
          window.location.href = '/login'
          throw new Error('登录已过期，请重新登录')
        }
        // 处理其他错误
        const errorText = await response.text()
        throw new Error(`请求失败: ${response.status} ${errorText || response.statusText}`)
      }
      
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.chunk) {
                fullResponse += data.chunk
                messages.value[aiMessageIndex].content = fullResponse
                if (onChunk) {
                  onChunk(data.chunk)
                }
              }
              if (data.done && data.conversation_id) {
                currentConversationId.value = data.conversation_id
                messages.value[aiMessageIndex].id = data.message_id || tempMessageId
              }
              if (data.error) {
                throw new Error(data.error)
              }
            } catch (e) {
              console.error('解析流数据失败:', e)
            }
          }
        }
      }
      
      return { response: fullResponse, conversation_id: currentConversationId.value }
    } catch (error) {
      console.error('流式发送消息失败:', error)
      // 移除失败的消息（如果存在）
      if (messages.value.length >= 2) {
        messages.value.pop()
        messages.value.pop()
      }
      
      // 如果是401错误，已经重定向，不需要显示错误消息
      if (error.message.includes('登录已过期') || error.message.includes('未登录')) {
        throw error
      }
      
      // 显示用户友好的错误消息
      throw new Error(error.message || '发送消息失败，请重试')
    } finally {
      loading.value = false
    }
  }

  function loadConversation(conversation) {
    currentConversationId.value = conversation.id
    messages.value = conversation.messages || []
    selectedScenario.value = conversation.scenario || 'general'
  }

  function clearMessages() {
    messages.value = []
    currentConversationId.value = null
  }

  function setScenario(scenario) {
    selectedScenario.value = scenario
  }

  return {
    conversations,
    currentConversationId,
    messages,
    loading,
    selectedScenario,
    scenarios,
    fetchConversations,
    sendMessage,
    sendMessageStream,
    loadConversation,
    clearMessages,
    setScenario
  }
})

