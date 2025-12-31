<template>
  <div class="dashboard-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">
            <span class="title-icon">📊</span>
            <span>学习进度</span>
          </h1>
          <p class="page-subtitle">追踪你的学习成果和进步</p>
        </div>
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="8" animated />
    </div>
    
    <!-- Dashboard Content -->
    <div v-else class="dashboard-content">
      <!-- Stats Grid -->
      <div class="stats-grid">
        <div class="stat-card" v-for="(stat, index) in stats" :key="index">
          <div class="stat-icon" :style="{ background: stat.gradient }">
            {{ stat.icon }}
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
          <div class="stat-trend" v-if="stat.trend">
            <el-icon><CaretTop v-if="stat.trend > 0" /><CaretBottom v-else /></el-icon>
            <span>{{ Math.abs(stat.trend) }}%</span>
          </div>
        </div>
      </div>
      
      <!-- Time Stats -->
      <div class="section-card">
        <div class="section-header">
          <h2 class="section-title">学习时长统计</h2>
        </div>
        
        <div class="time-stats-grid">
          <div class="time-stat-item" v-for="(item, index) in timeStats" :key="index">
            <div class="time-stat-header">
              <span class="time-stat-label">{{ item.label }}</span>
              <div class="time-stat-icon" :style="{ background: item.color }">
                {{ item.icon }}
              </div>
            </div>
            <div class="time-stat-value">{{ item.value }}</div>
            <div class="time-stat-bar">
              <div 
                class="time-stat-fill" 
                :style="{ width: item.percentage + '%', background: item.color }"
              ></div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Recent Activity -->
      <div class="section-card">
        <div class="section-header">
          <h2 class="section-title">最近活动</h2>
          <button class="view-all-btn" @click="$router.push('/voice')">
            <span>开始新对话</span>
            <el-icon><ArrowRight /></el-icon>
          </button>
        </div>
        
        <div v-if="recentConversations.length === 0" class="empty-state">
          <div class="empty-icon">💬</div>
          <div class="empty-text">还没有对话记录</div>
          <button class="empty-action" @click="$router.push('/voice')">
            开始你的第一次对话
          </button>
        </div>
        
        <div v-else class="activity-list-container" ref="activityListContainer" @scroll="handleScroll">
          <div class="activity-list">
            <div 
              class="activity-item" 
              v-for="conv in recentConversations" 
              :key="conv.id"
              @click="goToConversation(conv.id)"
            >
              <div class="activity-icon">
                {{ getScenarioIcon(conv.scenario) }}
              </div>
              <div class="activity-content">
                <div class="activity-header">
                  <span class="activity-title">{{ getScenarioLabel(conv.scenario) }}</span>
                  <span class="activity-meta">{{ conv.message_count }} 条消息</span>
                </div>
                <div class="activity-time">{{ formatDate(conv.started_at) }}</div>
              </div>
              <div class="activity-arrow">
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </div>
          
          <!-- 加载更多指示器 -->
          <div v-if="loadingMore" class="loading-more">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>加载中...</span>
          </div>
          
          <!-- 没有更多数据提示 -->
          <div v-if="!hasMore && recentConversations.length > 0" class="no-more">
            <span>没有更多数据了</span>
          </div>
        </div>
      </div>
      
      <!-- Achievements (Optional) -->
      <div class="section-card achievements">
        <div class="section-header">
          <h2 class="section-title">成就徽章</h2>
        </div>
        
        <div class="achievement-grid">
          <div 
            class="achievement-item" 
            v-for="achievement in achievements" 
            :key="achievement.id"
            :class="{ 'locked': !achievement.unlocked }"
          >
            <div class="achievement-icon">{{ achievement.icon }}</div>
            <div class="achievement-name">{{ achievement.name }}</div>
            <div class="achievement-desc">{{ achievement.description }}</div>
            <div v-if="!achievement.unlocked" class="achievement-lock">🔒</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import { ElMessage } from 'element-plus'
import { CaretTop, CaretBottom, ArrowRight, Loading } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(true)
const loadingMore = ref(false)
const hasMore = ref(true)
const currentPage = ref(0)
const pageSize = ref(10)
const activityListContainer = ref(null)

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
  general: { label: '日常对话', icon: '💬' },
  school: { label: '学校生活', icon: '🎓' },
  home: { label: '家庭生活', icon: '🏠' },
  shopping: { label: '购物', icon: '🛍️' },
  travel: { label: '旅行', icon: '✈️' }
}

const stats = computed(() => [
  {
    icon: '💬',
    label: '总对话数',
    value: progress.value.total_conversations,
    gradient: 'linear-gradient(135deg, #FF6B35 0%, #FF8557 100%)',
    trend: null
  },
  {
    icon: '⏱️',
    label: '总学习时长',
    value: formatTime(progress.value.total_time),
    gradient: 'linear-gradient(135deg, #00D9FF 0%, #0EA5E9 100%)',
    trend: null
  },
  {
    icon: '⭐',
    label: '平均评分',
    value: progress.value.average_score.toFixed(1),
    gradient: 'linear-gradient(135deg, #FFD23F 0%, #FBBF24 100%)',
    trend: null
  },
  {
    icon: '📅',
    label: '今日对话',
    value: progress.value.today_conversations,
    gradient: 'linear-gradient(135deg, #10B981 0%, #34D399 100%)',
    trend: null
  }
])

const timeStats = computed(() => {
  const maxTime = Math.max(
    progress.value.today_time,
    progress.value.weekly_time,
    progress.value.monthly_time,
    1
  )
  
  return [
    {
      label: '今日',
      icon: '📅',
      value: formatTime(progress.value.today_time),
      percentage: (progress.value.today_time / maxTime) * 100,
      color: 'linear-gradient(90deg, #FF6B35 0%, #FF8557 100%)'
    },
    {
      label: '本周',
      icon: '📊',
      value: formatTime(progress.value.weekly_time),
      percentage: (progress.value.weekly_time / maxTime) * 100,
      color: 'linear-gradient(90deg, #00D9FF 0%, #0EA5E9 100%)'
    },
    {
      label: '本月',
      icon: '📈',
      value: formatTime(progress.value.monthly_time),
      percentage: (progress.value.monthly_time / maxTime) * 100,
      color: 'linear-gradient(90deg, #FFD23F 0%, #FBBF24 100%)'
    }
  ]
})

const achievements = computed(() => [
  {
    id: 1,
    icon: '🎯',
    name: '初学者',
    description: '完成第一次对话',
    unlocked: progress.value.total_conversations >= 1
  },
  {
    id: 2,
    icon: '🔥',
    name: '坚持者',
    description: '连续学习7天',
    unlocked: false
  },
  {
    id: 3,
    icon: '🏆',
    name: '对话大师',
    description: '完成100次对话',
    unlocked: progress.value.total_conversations >= 100
  },
  {
    id: 4,
    icon: '⭐',
    name: '完美主义',
    description: '获得10次满分',
    unlocked: false
  },
  {
    id: 5,
    icon: '⏰',
    name: '时间管理',
    description: '累计学习10小时',
    unlocked: progress.value.total_time >= 36000
  },
  {
    id: 6,
    icon: '🚀',
    name: '进步飞快',
    description: '平均分超过85',
    unlocked: progress.value.average_score >= 85
  }
])

async function fetchProgress(reset = true) {
  try {
    if (reset) {
      loading.value = true
      currentPage.value = 0
      recentConversations.value = []
    } else {
      loadingMore.value = true
    }
    
    const offset = currentPage.value * pageSize.value
    const response = await api.get('/progress/')
    progress.value = response
    
    const statsResponse = await api.get(`/progress/stats?days=7&offset=${offset}&limit=${pageSize.value}`)
    
    if (reset) {
      recentConversations.value = statsResponse.recent_conversations || []
    } else {
      recentConversations.value.push(...(statsResponse.recent_conversations || []))
    }
    
    hasMore.value = statsResponse.has_more || false
    currentPage.value++
  } catch (error) {
    console.error('获取学习进度失败:', error)
    ElMessage.error('获取学习进度失败')
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

async function loadMore() {
  if (loadingMore.value || !hasMore.value) return
  await fetchProgress(false)
}

function handleScroll(event) {
  const container = event.target
  const scrollTop = container.scrollTop
  const scrollHeight = container.scrollHeight
  const clientHeight = container.clientHeight
  
  // 当滚动到距离底部50px时触发加载
  if (scrollHeight - scrollTop - clientHeight < 50) {
    loadMore()
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
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return date.toLocaleDateString('zh-CN')
}

function getScenarioLabel(scenario) {
  return scenarios[scenario]?.label || scenario
}

function getScenarioIcon(scenario) {
  return scenarios[scenario]?.icon || '💬'
}

function goToConversation(conversationId) {
  router.push(`/voice?id=${conversationId}`)
}

onMounted(() => {
  fetchProgress()
})
</script>

<style lang="scss" scoped>
.dashboard-page {
  min-height: calc(100vh - 72px);
  background: var(--bg-primary);
  
  @media (max-width: 768px) {
    min-height: calc(100vh - 64px);
  }
  
  @media (max-width: 860px) {
    // 为移动端底部导航预留空间已在Layout中处理
    min-height: calc(100vh - 64px - 72px);
  }
}

.page-header {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  padding: var(--space-2xl) var(--space-xl);
  
  @media (max-width: 768px) {
    padding: var(--space-xl) var(--space-lg);
  }
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
}

.page-title {
  font-family: var(--font-display);
  font-size: 2rem;
  font-weight: 800;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin: 0 0 var(--space-sm) 0;
  
  .title-icon {
    font-size: 2.5rem;
  }
}

.page-subtitle {
  color: var(--text-secondary);
  font-size: 1rem;
  margin: 0;
}

.loading-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: var(--space-2xl) var(--space-xl);
}

.dashboard-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: var(--space-2xl) var(--space-xl);
  display: flex;
  flex-direction: column;
  gap: var(--space-2xl);
  
  @media (max-width: 768px) {
    padding: var(--space-xl) var(--space-lg);
    gap: var(--space-xl);
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: var(--space-lg);
  
  @media (max-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-md);
  }
  
  @media (max-width: 480px) {
    grid-template-columns: 1fr;
  }
}

.stat-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-2xl);
  padding: var(--space-xl);
  box-shadow: var(--shadow-md);
  display: flex;
  align-items: center;
  gap: var(--space-lg);
  transition: all var(--transition-base);
  position: relative;
  overflow: hidden;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
  }
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  box-shadow: var(--shadow-md);
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-family: var(--font-display);
  font-size: 2rem;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1;
  margin-bottom: var(--space-xs);
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--success);
}

.section-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-2xl);
  padding: var(--space-2xl);
  box-shadow: var(--shadow-md);
  
  @media (max-width: 768px) {
    padding: var(--space-xl);
  }
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-xl);
}

.section-title {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.view-all-btn {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-lg);
  background: transparent;
  border: 2px solid var(--border-color);
  border-radius: var(--radius-lg);
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all var(--transition-base);
  font-family: var(--font-body);
  
  &:hover {
    border-color: var(--primary);
    color: var(--primary);
    background: rgba(255, 107, 53, 0.05);
  }
}

.time-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-xl);
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

.time-stat-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.time-stat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.time-stat-label {
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.time-stat-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.time-stat-value {
  font-family: var(--font-display);
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--text-primary);
}

.time-stat-bar {
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.time-stat-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--transition-slow);
}

.empty-state {
  text-align: center;
  padding: var(--space-3xl) var(--space-2xl);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: var(--space-lg);
  opacity: 0.5;
}

.empty-text {
  font-size: 1.125rem;
  color: var(--text-tertiary);
  margin-bottom: var(--space-xl);
}

.empty-action {
  padding: var(--space-md) var(--space-2xl);
  background: var(--bg-gradient-primary);
  border: none;
  border-radius: var(--radius-lg);
  color: var(--text-inverse);
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all var(--transition-base);
  box-shadow: var(--shadow-colored);
  font-family: var(--font-body);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-xl);
  }
}

.activity-list-container {
  max-height: 600px;
  overflow-y: auto;
  padding-right: var(--space-sm);
  
  /* 自定义滚动条样式 */
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: var(--bg-tertiary);
    border-radius: var(--radius-full);
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--neutral-300);
    border-radius: var(--radius-full);
    
    &:hover {
      background: var(--neutral-400);
    }
  }
  
  @media (max-width: 768px) {
    max-height: 500px;
  }
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.activity-item {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
  padding: var(--space-lg);
  background: var(--bg-tertiary);
  border-radius: var(--radius-xl);
  cursor: pointer;
  transition: all var(--transition-base);
  
  &:hover {
    background: var(--bg-primary);
    transform: translateX(8px);
    box-shadow: var(--shadow-sm);
  }
}

.activity-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  background: var(--bg-gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
  margin-bottom: var(--space-xs);
}

.activity-title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 1rem;
}

.activity-meta {
  font-size: 0.8125rem;
  color: var(--text-tertiary);
}

.activity-time {
  font-size: 0.8125rem;
  color: var(--text-tertiary);
}

.activity-arrow {
  color: var(--text-tertiary);
  font-size: 1.25rem;
  flex-shrink: 0;
  transition: transform var(--transition-base);
  
  .activity-item:hover & {
    transform: translateX(4px);
    color: var(--primary);
  }
}

.achievement-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: var(--space-lg);
  
  @media (max-width: 768px) {
    grid-template-columns: repeat(3, 1fr);
  }
  
  @media (max-width: 480px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

.achievement-item {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: var(--space-lg);
  background: var(--bg-tertiary);
  border-radius: var(--radius-xl);
  transition: all var(--transition-base);
  
  &:hover:not(.locked) {
    transform: translateY(-4px);
    box-shadow: var(--shadow-md);
  }
  
  &.locked {
    opacity: 0.5;
    filter: grayscale(1);
  }
}

.achievement-icon {
  font-size: 2.5rem;
  margin-bottom: var(--space-md);
}

.achievement-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.875rem;
  margin-bottom: var(--space-xs);
}

.achievement-desc {
  font-size: 0.75rem;
  color: var(--text-tertiary);
}

.achievement-lock {
  position: absolute;
  top: var(--space-sm);
  right: var(--space-sm);
  font-size: 1rem;
}

.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  padding: var(--space-xl);
  color: var(--text-secondary);
  font-size: 0.875rem;
  
  .el-icon {
    font-size: 1.25rem;
  }
}

.no-more {
  text-align: center;
  padding: var(--space-xl);
  color: var(--text-tertiary);
  font-size: 0.875rem;
  border-top: 1px solid var(--border-color);
  margin-top: var(--space-md);
}
</style>


