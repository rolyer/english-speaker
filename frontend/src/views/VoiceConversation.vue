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
        
        <!-- 最近的对话内容（语音气泡样式） -->
        <div class="recent-messages">
          <div
            v-for="message in recentMessages"
            :key="message.id"
            :class="['voice-message-row', message.role]"
          >
            <!-- 用户消息：头像在右侧 -->
            <template v-if="message.role === 'user'">
              <!-- 用户头像 -->
              <div class="message-avatar user-avatar">
                <span>👤</span>
              </div>
              
              <!-- 消息卡片 -->
              <div class="message-card user-card">
                <div class="card-content">
                  <!-- 语音气泡 -->
                  <div class="voice-bubble user-bubble" @click="playUserAudio(message)">
                    <el-icon class="play-icon" :class="{ 'playing': isPlayingMessage(message.id) }">
                      <VideoPlay v-if="!isPlayingMessage(message.id)" />
                      <VideoPause v-else />
                    </el-icon>
                    <div class="sound-wave-mini" :class="{ 'active': isPlayingMessage(message.id) }">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                    <span class="voice-duration">{{ getAudioDuration(message) }}"</span>
                    
                    <!-- 发音评分（紧凑显示） -->
                    <div v-if="message.pronunciation_score !== null && message.pronunciation_score !== undefined" class="score-badge">
                      {{ message.pronunciation_score }}
                    </div>
                  </div>
                  
                  <!-- 底部操作栏 -->
                  <div class="card-actions">
                    <div class="message-time">{{ formatTime(message.created_at) }}</div>
                    <el-dropdown trigger="click" @command="(cmd) => handleMessageCommand(cmd, message)">
                      <el-button text circle size="small" class="message-menu-btn">
                        <el-icon><MoreFilled /></el-icon>
                      </el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item :command="'toggleText'">
                            <el-icon><Document /></el-icon>
                            {{ messageStates[message.id]?.showText ? '隐藏文本' : '显示文本' }}
                          </el-dropdown-item>
                          <el-dropdown-item :command="'translate'" :disabled="messageStates[message.id]?.translating">
                            <el-icon><Connection /></el-icon>
                            {{ messageStates[message.id]?.translation ? '隐藏翻译' : '显示翻译' }}
                          </el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>
                </div>
                
                <!-- 展开的内容 -->
                <div v-if="messageStates[message.id]?.showText || messageStates[message.id]?.translation" class="expanded-content">
                  <div v-if="messageStates[message.id]?.showText" class="transcription" v-html="formatMessage(message.content)"></div>
                  <div v-if="messageStates[message.id]?.translation" class="translation">
                    <div class="translation-label">翻译：</div>
                    <div class="translation-content" v-html="formatMessage(messageStates[message.id].translation)"></div>
                  </div>
                </div>
              </div>
            </template>
            
            <!-- AI 消息：头像在左侧 -->
            <template v-else>
              <!-- AI 头像 -->
              <div class="message-avatar ai-avatar">
                <span>🤖</span>
              </div>
              
              <!-- 消息卡片 -->
              <div class="message-card ai-card">
                <!-- 隐藏的 AudioPlayer 用于音频控制 -->
                <AudioPlayer
                  :ref="el => { if (el) audioPlayerRefs[message.id] = el }"
                  :text="message.content"
                  :auto-play="false"
                  @play="handleAIPlay"
                  @pause="handleAIPause"
                  @end="handleAIEnd"
                  style="display: none;"
                />
                
                <div class="card-content">
                  <!-- 语音气泡 -->
                  <div class="voice-bubble ai-bubble" @click="playAIAudio(message)">
                    <el-icon class="play-icon" :class="{ 'playing': isPlayingMessage(message.id) }">
                      <VideoPlay v-if="!isPlayingMessage(message.id)" />
                      <VideoPause v-else />
                    </el-icon>
                    <div class="sound-wave-mini" :class="{ 'active': isPlayingMessage(message.id) }">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                    <span class="voice-duration">{{ getAudioDuration(message) }}"</span>
                  </div>
                  
                  <!-- 底部操作栏 -->
                  <div class="card-actions">
                    <div class="message-time">{{ formatTime(message.created_at) }}</div>
                    <el-dropdown trigger="click" @command="(cmd) => handleMessageCommand(cmd, message)">
                      <el-button text circle size="small" class="message-menu-btn">
                        <el-icon><MoreFilled /></el-icon>
                      </el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item :command="'toggleText'">
                            <el-icon><Document /></el-icon>
                            {{ messageStates[message.id]?.showText ? '隐藏文本' : '显示文本' }}
                          </el-dropdown-item>
                          <el-dropdown-item :command="'translate'" :disabled="messageStates[message.id]?.translating">
                            <el-icon><Connection /></el-icon>
                            {{ messageStates[message.id]?.translation ? '隐藏翻译' : '显示翻译' }}
                          </el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>
                </div>
                
                <!-- 展开的内容 -->
                <div v-if="messageStates[message.id]?.showText || messageStates[message.id]?.translation" class="expanded-content">
                  <div v-if="messageStates[message.id]?.showText" class="transcription" v-html="formatMessage(message.content)"></div>
                  <div v-if="messageStates[message.id]?.translation" class="translation">
                    <div class="translation-label">翻译：</div>
                    <div class="translation-content" v-html="formatMessage(messageStates[message.id].translation)"></div>
                  </div>
                </div>
              </div>
            </template>
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
import { ref, computed, nextTick, onMounted, onUnmounted, watch, reactive } from 'vue'
import { useChatStore } from '@/stores/chat'
import { isMobile } from '@/utils/device'
import { ElMessage } from 'element-plus'
import { Position, MoreFilled, Document, Connection, VideoPlay, VideoPause } from '@element-plus/icons-vue'
import AudioRecorder from '@/components/AudioRecorder.vue'
import AudioPlayer from '@/components/AudioPlayer.vue'
import PronunciationScore from '@/components/PronunciationScore.vue'
import api from '@/services/api'
import axios from 'axios'

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
const currentPlayingId = ref(null) // 当前正在播放的消息ID
const audioCache = new Map() // 音频缓存

// 每条消息的状态（显示文本、翻译等）
const messageStates = reactive({})

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
  if (!content) return ''
  
  // 转义 HTML 特殊字符
  let formatted = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  
  // 处理 Markdown 语法（注意顺序很重要）
  
  // 1. 行内代码：`code`（先处理，避免代码内的 * 被误解析）
  formatted = formatted.replace(/`([^`]+?)`/g, '<code>$1</code>')
  
  // 2. 加粗：**text** 或 __text__（必须在斜体之前处理）
  formatted = formatted.replace(/\*\*([^*]+?)\*\*/g, '<strong>$1</strong>')
  formatted = formatted.replace(/__([^_]+?)__/g, '<strong>$1</strong>')
  
  // 3. 斜体：*text* 或 _text_
  formatted = formatted.replace(/\*([^*]+?)\*/g, '<em>$1</em>')
  formatted = formatted.replace(/_([^_]+?)_/g, '<em>$1</em>')
  
  // 4. 删除线：~~text~~
  formatted = formatted.replace(/~~([^~]+?)~~/g, '<del>$1</del>')
  
  // 5. 换行：\n
  formatted = formatted.replace(/\n/g, '<br>')
  
  return formatted
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
  // 播放结束时清除当前播放ID
  currentPlayingId.value = null
}

function toggleHistoryView() {
  showFullHistory.value = !showFullHistory.value
  nextTick(() => {
    scrollToBottom()
  })
}

// 初始化消息状态
function initMessageState(messageId) {
  if (!messageStates[messageId]) {
    messageStates[messageId] = {
      showText: false,
      translation: null,
      translating: false
    }
  }
}

// 处理消息菜单命令
async function handleMessageCommand(command, message) {
  initMessageState(message.id)
  
  if (command === 'toggleText') {
    // 切换文本显示
    messageStates[message.id].showText = !messageStates[message.id].showText
  } else if (command === 'translate') {
    // 切换翻译
    if (messageStates[message.id].translation) {
      // 如果已有翻译，则隐藏
      messageStates[message.id].translation = null
    } else {
      // 否则请求翻译
      await translateMessage(message)
    }
  }
}

// 翻译消息
async function translateMessage(message) {
  initMessageState(message.id)
  
  if (messageStates[message.id].translating) {
    return
  }
  
  messageStates[message.id].translating = true
  
  try {
    // 调用翻译 API
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

// 判断消息是否正在播放
function isPlayingMessage(messageId) {
  return currentPlayingId.value === messageId
}

// 获取音频时长（估算：按字数计算，平均每个字0.3秒）
function getAudioDuration(message) {
  if (!message.content) return 0
  // 简单估算：英文按单词数，中文按字数
  const words = message.content.split(/\s+/).length
  const duration = Math.max(1, Math.ceil(words * 0.5)) // 每个单词约0.5秒
  return Math.min(60, duration) // 最多显示60秒
}

// 播放用户音频
async function playUserAudio(message) {
  // 用户消息没有实际音频，这里可以播放TTS
  if (currentPlayingId.value === message.id) {
    // 如果正在播放，则停止
    stopAudio()
  } else {
    await playMessageAudio(message)
  }
}

// 播放AI音频
async function playAIAudio(message) {
  if (currentPlayingId.value === message.id) {
    // 如果正在播放，则停止
    stopAudio()
  } else {
    await playMessageAudio(message)
  }
}

// 播放消息音频
async function playMessageAudio(message) {
  try {
    // 先停止当前正在播放的音频
    if (currentPlayingId.value && currentPlayingId.value !== message.id) {
      stopAudio()
    }
    
    currentPlayingId.value = message.id
    
    // 使用 AudioPlayer 组件的引用播放
    const audioPlayer = audioPlayerRefs.value[message.id]
    if (audioPlayer && typeof audioPlayer.play === 'function') {
      await audioPlayer.play()
      // AudioPlayer 的 end 事件会触发 handleAIEnd，那里会清除 currentPlayingId
    } else {
      // 如果没有 AudioPlayer 引用，直接调用 TTS API
      const response = await axios.post('/api/tts/synthesize', {
        text: message.content,
        language: 'en-US'
      }, {
        responseType: 'blob'
      })
      
      const audioBlob = response.data
      const audioUrl = URL.createObjectURL(audioBlob)
      
      // 创建音频元素播放
      const audio = new Audio(audioUrl)
      audioCache.set(message.id, audio)
      
      audio.onended = () => {
        currentPlayingId.value = null
        URL.revokeObjectURL(audioUrl)
      }
      
      audio.onerror = () => {
        currentPlayingId.value = null
        URL.revokeObjectURL(audioUrl)
        ElMessage.error('音频播放失败')
      }
      
      await audio.play()
    }
  } catch (error) {
    console.error('播放音频失败:', error)
    currentPlayingId.value = null
    if (error.name !== 'NotAllowedError') {
      ElMessage.error('音频播放失败')
    }
  }
}

// 停止音频播放
function stopAudio() {
  if (currentPlayingId.value) {
    const playingId = currentPlayingId.value
    
    // 停止直接创建的 Audio 元素
    const audio = audioCache.get(playingId)
    if (audio) {
      audio.pause()
      audio.currentTime = 0
    }
    
    // 停止 AudioPlayer 组件
    const audioPlayer = audioPlayerRefs.value[playingId]
    if (audioPlayer && typeof audioPlayer.pause === 'function') {
      audioPlayer.pause()
    }
    
    // 清除播放状态
    currentPlayingId.value = null
    isAISpeaking.value = false
  }
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

// 最近的消息 - 语音气泡样式
.recent-messages {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.voice-message-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  animation: slideUp 0.3s ease-out;
  
  &.user {
    flex-direction: row-reverse;
  }
  
  &.assistant {
    flex-direction: row;
  }
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
  
  &.user-avatar {
    background: linear-gradient(135deg, var(--primary-color), #ff8fab);
  }
  
  &.ai-avatar {
    background: linear-gradient(135deg, #667eea, #764ba2);
  }
  
  @media (max-width: 768px) {
    width: 36px;
    height: 36px;
    font-size: 20px;
  }
}

// 消息卡片容器
.message-card {
  flex: 1;
  max-width: 70%;
  background: white;
  border-radius: 16px;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.2s ease;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  }
  
  @media (max-width: 768px) {
    max-width: 75%;
    padding: 10px;
  }
  
  &.user-card {
    background: linear-gradient(135deg, rgba(255, 107, 157, 0.05), rgba(255, 139, 171, 0.05));
    border: 1px solid rgba(255, 107, 157, 0.1);
  }
  
  &.ai-card {
    background: white;
    border: 1px solid var(--border-color);
  }
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.card-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 4px;
  padding-top: 8px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.voice-bubble {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 18px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 120px;
  
  &:hover {
    transform: translateY(-1px);
  }
  
  &:active {
    transform: scale(0.98);
  }
  
  &.user-bubble {
    background: linear-gradient(135deg, var(--primary-color), #ff8fab);
    color: white;
    box-shadow: 0 2px 6px rgba(255, 107, 157, 0.3);
  }
  
  &.ai-bubble {
    background: #f5f7fa;
    color: var(--text-color);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  }
  
  .play-icon {
    font-size: 22px;
    flex-shrink: 0;
    transition: transform 0.2s ease;
    
    &.playing {
      animation: pulse 1.5s infinite;
    }
  }
  
  .sound-wave-mini {
    display: flex;
    gap: 2px;
    align-items: center;
    height: 20px;
    
    span {
      width: 2px;
      height: 8px;
      background: currentColor;
      border-radius: 1px;
      opacity: 0.3;
      transition: all 0.2s ease;
    }
    
    &.active span {
      opacity: 1;
      animation: soundWaveMini 0.8s infinite ease-in-out;
      
      &:nth-child(1) { animation-delay: 0s; }
      &:nth-child(2) { animation-delay: 0.1s; }
      &:nth-child(3) { animation-delay: 0.2s; }
    }
  }
  
  .voice-duration {
    font-size: 0.85rem;
    font-weight: 500;
    margin-left: auto;
  }
  
  .score-badge {
    position: absolute;
    top: -6px;
    right: -6px;
    background: #4caf50;
    color: white;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }
}

@keyframes soundWaveMini {
  0%, 100% {
    height: 8px;
  }
  50% {
    height: 16px;
  }
}

.message-time {
  font-size: 0.75rem;
  color: var(--text-light);
  opacity: 0.7;
}

.message-menu-btn {
  opacity: 0.6;
  transition: opacity 0.2s;
  
  &:hover {
    opacity: 1;
  }
}

.expanded-content {
  width: 100%;
  animation: fadeIn 0.3s ease-out;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  
  .transcription {
    font-size: 0.9rem;
    color: var(--text-color);
    line-height: 1.6;
    padding: 10px 12px;
    background: rgba(0, 0, 0, 0.02);
    border-radius: 10px;
    margin-bottom: 8px;
    
    // 支持 HTML 格式
    p {
      margin: 0.5em 0;
      
      &:first-child {
        margin-top: 0;
      }
      
      &:last-child {
        margin-bottom: 0;
      }
    }
    
    strong {
      font-weight: 600;
      color: var(--text-color);
    }
    
    em {
      font-style: italic;
    }
    
    del {
      text-decoration: line-through;
      opacity: 0.7;
    }
    
    code {
      background: rgba(0, 0, 0, 0.1);
      padding: 2px 4px;
      border-radius: 3px;
      font-family: monospace;
      font-size: 0.85em;
    }
  }
  
  .translation {
    padding: 10px 12px;
    background: #e3f2fd;
    border-radius: 10px;
    border-left: 3px solid #2196f3;
    
    .translation-label {
      font-size: 0.75rem;
      color: #2196f3;
      font-weight: 600;
      margin-bottom: 4px;
    }
    
    .translation-content {
      font-size: 0.9rem;
      color: var(--text-color);
      line-height: 1.6;
      
      // 支持 HTML 格式
      p {
        margin: 0.5em 0;
        
        &:first-child {
          margin-top: 0;
        }
        
        &:last-child {
          margin-bottom: 0;
        }
      }
      
      strong {
        font-weight: 600;
      }
      
      em {
        font-style: italic;
      }
      
      del {
        text-decoration: line-through;
        opacity: 0.7;
      }
      
      code {
        background: rgba(0, 0, 0, 0.05);
        padding: 2px 4px;
        border-radius: 3px;
        font-family: monospace;
        font-size: 0.85em;
      }
    }
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

