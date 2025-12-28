<template>
  <div class="dashboard-page">
    <div class="dashboard-header">
      <h2>📊 学习进度</h2>
    </div>
    
    <div v-if="loading" class="loading">
      <el-skeleton :rows="5" animated />
    </div>
    
    <div v-else class="dashboard-content">
      <!-- 总体统计 -->
      <div class="stats-grid">
        <div class="stat-card card">
          <div class="stat-icon">💬</div>
          <div class="stat-value">{{ progress.total_conversations }}</div>
          <div class="stat-label">总对话数</div>
        </div>
        
        <div class="stat-card card">
          <div class="stat-icon">⏱️</div>
          <div class="stat-value">{{ formatTime(progress.total_time) }}</div>
          <div class="stat-label">总学习时长</div>
        </div>
        
        <div class="stat-card card">
          <div class="stat-icon">⭐</div>
          <div class="stat-value">{{ progress.average_score.toFixed(1) }}</div>
          <div class="stat-label">平均评分</div>
        </div>
        
        <div class="stat-card card">
          <div class="stat-icon">📅</div>
          <div class="stat-value">{{ progress.today_conversations }}</div>
          <div class="stat-label">今日对话</div>
        </div>
      </div>
      
      <!-- 时间统计 -->
      <div class="time-stats card">
        <h3>时间统计</h3>
        <div class="time-grid">
          <div class="time-item">
            <span class="time-label">今日</span>
            <span class="time-value">{{ formatTime(progress.today_time) }}</span>
          </div>
          <div class="time-item">
            <span class="time-label">本周</span>
            <span class="time-value">{{ formatTime(progress.weekly_time) }}</span>
          </div>
          <div class="time-item">
            <span class="time-label">本月</span>
            <span class="time-value">{{ formatTime(progress.monthly_time) }}</span>
          </div>
        </div>
      </div>
      
      <!-- 最近对话 -->
      <div class="recent-conversations card">
        <h3>最近对话</h3>
        <div v-if="recentConversations.length === 0" class="empty">
          还没有对话记录，快去开始练习吧！
        </div>
        <div v-else class="conversation-list">
          <div
            v-for="conv in recentConversations"
            :key="conv.id"
            class="conversation-item"
            @click="goToConversation(conv.id)"
          >
            <div class="conv-info">
              <span class="conv-scenario">{{ getScenarioLabel(conv.scenario) }}</span>
              <span class="conv-time">{{ formatDate(conv.started_at) }}</span>
            </div>
            <div class="conv-meta">
              <span>{{ conv.message_count }} 条消息</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(true)
const progress = ref({
  total_conversations: 0,
  total_time: 0,
  average_score: 0,
  today_conversations: 0,
  today_time: 0,
  weekly_conversations: 0,
  weekly_time: 0,
  monthly_conversations: 0,
  monthly_time: 0
})
const recentConversations = ref([])

const scenarios = {
  general: '日常对话',
  school: '学校生活',
  home: '家庭生活',
  shopping: '购物',
  travel: '旅行'
}

async function fetchProgress() {
  try {
    loading.value = true
    const response = await api.get('/progress/')
    progress.value = response
    
    const statsResponse = await api.get('/progress/stats?days=7')
    recentConversations.value = statsResponse.recent_conversations || []
  } catch (error) {
    console.error('获取学习进度失败:', error)
    ElMessage.error('获取学习进度失败')
  } finally {
    loading.value = false
  }
}

function formatTime(seconds) {
  if (!seconds) return '0分钟'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  }
  return `${minutes}分钟`
}

function formatDate(dateString) {
  const date = new Date(dateString)
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

function getScenarioLabel(scenario) {
  return scenarios[scenario] || scenario
}

function goToConversation(conversationId) {
  router.push(`/conversation?id=${conversationId}`)
}

onMounted(() => {
  fetchProgress()
})
</script>

<style lang="scss" scoped>
.dashboard-page {
  min-height: calc(100vh - 64px);
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  
  @media (max-width: 768px) {
    min-height: calc(100vh - 56px); // 移动端顶部导航高度
    padding: 16px;
  }
}

.dashboard-header {
  margin-bottom: 24px;
  
  h2 {
    margin: 0;
    color: var(--primary-color);
    font-size: 1.8rem;
  }
}

.loading {
  padding: 20px;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  
  @media (max-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

.stat-card {
  text-align: center;
  padding: 24px;
  
  .stat-icon {
    font-size: 2.5rem;
    margin-bottom: 12px;
  }
  
  .stat-value {
    font-size: 2rem;
    font-weight: bold;
    color: var(--primary-color);
    margin-bottom: 8px;
  }
  
  .stat-label {
    color: var(--text-light);
    font-size: 0.9rem;
  }
}

.time-stats {
  padding: 20px;
  
  h3 {
    margin: 0 0 16px 0;
    color: var(--text-color);
  }
}

.time-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

.time-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  background: var(--bg-light);
  border-radius: 8px;
  
  .time-label {
    color: var(--text-light);
    font-size: 0.9rem;
    margin-bottom: 8px;
  }
  
  .time-value {
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--primary-color);
  }
}

.recent-conversations {
  padding: 20px;
  
  h3 {
    margin: 0 0 16px 0;
    color: var(--text-color);
  }
}

.empty {
  text-align: center;
  padding: 40px;
  color: var(--text-light);
}

.conversation-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.conversation-item {
  padding: 16px;
  background: var(--bg-light);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  
  &:hover {
    background: var(--border-color);
    transform: translateX(4px);
  }
  
  .conv-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    
    .conv-scenario {
      font-weight: 500;
      color: var(--text-color);
    }
    
    .conv-time {
      color: var(--text-light);
      font-size: 0.85rem;
    }
  }
  
  .conv-meta {
    color: var(--text-light);
    font-size: 0.85rem;
  }
}
</style>
