<template>
  <div class="home-page">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-background">
        <div class="blob blob-1"></div>
        <div class="blob blob-2"></div>
        <div class="blob blob-3"></div>
      </div>
      
      <div class="hero-content">
        <div class="hero-badge animate-slide-down">
          <span class="badge-icon">🚀</span>
          <span class="badge-text">AI驱动的口语训练平台</span>
        </div>
        
        <h1 class="hero-title animate-slide-up">
          开启你的
          <span class="text-gradient">英语口语</span>
          学习之旅
        </h1>
        
        <p class="hero-subtitle animate-slide-up" style="animation-delay: 0.1s;">
          通过AI智能对话，让英语学习变得简单、有趣、高效
        </p>
        
        <div class="hero-actions animate-slide-up" style="animation-delay: 0.2s;">
          <el-button
            v-if="!userStore.isAuthenticated"
            type="primary"
            size="large"
            class="cta-button"
            @click="$router.push('/login')"
          >
            <span class="button-content">
              <span>开始学习</span>
              <el-icon class="button-icon"><Right /></el-icon>
            </span>
          </el-button>
          <el-button
            v-else
            type="primary"
            size="large"
            class="cta-button"
            @click="$router.push('/voice')"
          >
            <span class="button-content">
              <span>开始对话</span>
              <el-icon class="button-icon"><Right /></el-icon>
            </span>
          </el-button>
          
          <button class="demo-button" @click="scrollToFeatures">
            <span>了解更多</span>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M10 3V17M10 17L16 11M10 17L4 11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
        
        <!-- Stats -->
        <div class="hero-stats animate-slide-up" style="animation-delay: 0.3s;">
          <div class="stat-item">
            <div class="stat-value">10,000+</div>
            <div class="stat-label">学习者</div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <div class="stat-value">50+</div>
            <div class="stat-label">学习场景</div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <div class="stat-value">98%</div>
            <div class="stat-label">满意度</div>
          </div>
        </div>
      </div>
      
      <!-- Floating elements -->
      <div class="floating-elements">
        <div class="float-card card-1 animate-float" style="animation-delay: 0s;">
          <div class="float-icon">🎯</div>
          <div class="float-text">个性化学习</div>
        </div>
        <div class="float-card card-2 animate-float" style="animation-delay: 0.5s;">
          <div class="float-icon">⚡</div>
          <div class="float-text">即时反馈</div>
        </div>
        <div class="float-card card-3 animate-float" style="animation-delay: 1s;">
          <div class="float-icon">🏆</div>
          <div class="float-text">成就系统</div>
        </div>
      </div>
    </section>
    
    <!-- Features Section -->
    <section class="features" ref="featuresSection">
      <div class="section-header">
        <div class="section-badge">
          <span>✨ 核心功能</span>
        </div>
        <h2 class="section-title">为什么选择我们</h2>
        <p class="section-subtitle">AI技术驱动，为你打造最佳的口语学习体验</p>
      </div>
      
      <div class="features-grid">
        <div class="feature-card" v-for="(feature, index) in features" :key="index">
          <div class="feature-icon-wrapper">
            <div class="feature-icon" :style="{ background: feature.gradient }">
              {{ feature.icon }}
            </div>
          </div>
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-description">{{ feature.description }}</p>
        </div>
      </div>
    </section>
    
    <!-- How it works -->
    <section class="how-it-works">
      <div class="section-header">
        <div class="section-badge">
          <span>📚 学习流程</span>
        </div>
        <h2 class="section-title">三步开始你的学习</h2>
      </div>
      
      <div class="steps-container">
        <div class="step" v-for="(step, index) in steps" :key="index">
          <div class="step-number">{{ index + 1 }}</div>
          <div class="step-content">
            <div class="step-icon">{{ step.icon }}</div>
            <h3 class="step-title">{{ step.title }}</h3>
            <p class="step-description">{{ step.description }}</p>
          </div>
          <div v-if="index < steps.length - 1" class="step-arrow">→</div>
        </div>
      </div>
    </section>
    
    <!-- CTA Section -->
    <section class="cta-section">
      <div class="cta-content">
        <h2 class="cta-title">准备好开始学习了吗？</h2>
        <p class="cta-subtitle">加入我们，让AI助力你的英语学习之旅</p>
        <el-button
          v-if="!userStore.isAuthenticated"
          type="primary"
          size="large"
          class="cta-button-large"
          @click="$router.push('/login')"
        >
          <span class="button-content">
            <span>立即开始</span>
            <el-icon class="button-icon"><Right /></el-icon>
          </span>
        </el-button>
        <el-button
          v-else
          type="primary"
          size="large"
          class="cta-button-large"
          @click="$router.push('/voice')"
        >
          <span class="button-content">
            <span>开始对话</span>
            <el-icon class="button-icon"><Right /></el-icon>
          </span>
        </el-button>
      </div>
      
      <div class="cta-decoration">
        <div class="decoration-circle circle-1"></div>
        <div class="decoration-circle circle-2"></div>
        <div class="decoration-circle circle-3"></div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'
import { Right } from '@element-plus/icons-vue'

const userStore = useUserStore()
const featuresSection = ref(null)

const features = [
  {
    icon: '🎤',
    title: 'AI语音对话',
    description: '与AI进行真实对话练习，提升口语表达能力',
    gradient: 'linear-gradient(135deg, #FF6B35 0%, #FF8557 100%)'
  },
  {
    icon: '🎯',
    title: '智能发音评分',
    description: '实时评估发音准确度，提供改进建议',
    gradient: 'linear-gradient(135deg, #00D9FF 0%, #0EA5E9 100%)'
  },
  {
    icon: '📚',
    title: '多样化场景',
    description: '涵盖日常、商务、旅游等50+学习场景',
    gradient: 'linear-gradient(135deg, #FFD23F 0%, #FBBF24 100%)'
  },
  {
    icon: '📊',
    title: '学习进度追踪',
    description: '可视化学习数据，清晰了解学习成果',
    gradient: 'linear-gradient(135deg, #10B981 0%, #34D399 100%)'
  },
  {
    icon: '🔄',
    title: '实时翻译',
    description: '即时翻译对话内容，加深理解',
    gradient: 'linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%)'
  },
  {
    icon: '⚡',
    title: '快速反馈',
    description: 'AI秒级响应，流畅的对话体验',
    gradient: 'linear-gradient(135deg, #F59E0B 0%, #FCD34D 100%)'
  }
]

const steps = [
  {
    icon: '📝',
    title: '注册账号',
    description: '快速创建你的学习账号'
  },
  {
    icon: '🎭',
    title: '选择场景',
    description: '从多个场景中选择你想练习的'
  },
  {
    icon: '🚀',
    title: '开始对话',
    description: '与AI进行实时语音对话练习'
  }
]

function scrollToFeatures() {
  featuresSection.value?.scrollIntoView({ behavior: 'smooth' })
}
</script>

<style lang="scss" scoped>
.home-page {
  min-height: 100vh;
  overflow-x: hidden;
}

/* Hero Section */
.hero {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-3xl) var(--space-xl);
  overflow: hidden;
  
  @media (max-width: 768px) {
    min-height: 90vh;
    padding: var(--space-2xl) var(--space-lg);
  }
}

.hero-background {
  position: absolute;
  inset: 0;
  z-index: 0;
  overflow: hidden;
  background: linear-gradient(135deg, 
    rgba(255, 107, 53, 0.05) 0%, 
    rgba(0, 217, 255, 0.05) 50%, 
    rgba(255, 210, 63, 0.05) 100%);
  
  .blob {
    position: absolute;
    border-radius: 50%;
    filter: blur(60px);
    opacity: 0.3;
    animation: float 20s ease-in-out infinite;
  }
  
  .blob-1 {
    width: 500px;
    height: 500px;
    background: var(--primary);
    top: -100px;
    left: -100px;
    animation-delay: 0s;
  }
  
  .blob-2 {
    width: 400px;
    height: 400px;
    background: var(--secondary);
    bottom: -100px;
    right: -100px;
    animation-delay: 5s;
  }
  
  .blob-3 {
    width: 300px;
    height: 300px;
    background: var(--accent);
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    animation-delay: 10s;
  }
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 900px;
  text-align: center;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-lg);
  background: var(--bg-secondary);
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-md);
  margin-bottom: var(--space-xl);
  
  .badge-icon {
    font-size: 1.25rem;
  }
  
  .badge-text {
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 0.875rem;
    color: var(--text-secondary);
  }
}

.hero-title {
  font-family: var(--font-display);
  font-size: clamp(2.5rem, 6vw, 4.5rem);
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: var(--space-lg);
  color: var(--text-primary);
  
  .text-gradient {
    display: inline-block;
    background: var(--bg-gradient-hero);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
}

.hero-subtitle {
  font-size: clamp(1.125rem, 2vw, 1.5rem);
  color: var(--text-secondary);
  margin-bottom: var(--space-2xl);
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-lg);
  margin-bottom: var(--space-3xl);
  
  @media (max-width: 768px) {
    flex-direction: column;
    gap: var(--space-md);
  }
}

.cta-button {
  padding: var(--space-lg) var(--space-2xl);
  font-size: 1.125rem;
  font-weight: 600;
  border-radius: var(--radius-xl);
  height: auto;
  
  .button-content {
    display: flex;
    align-items: center;
    gap: var(--space-sm);
  }
  
  .button-icon {
    transition: transform var(--transition-base);
  }
  
  &:hover .button-icon {
    transform: translateX(4px);
  }
}

.demo-button {
  padding: var(--space-lg) var(--space-xl);
  font-size: 1.125rem;
  font-weight: 500;
  background: transparent;
  border: 2px solid var(--border-color);
  border-radius: var(--radius-xl);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  transition: all var(--transition-base);
  font-family: var(--font-body);
  
  &:hover {
    border-color: var(--primary);
    color: var(--primary);
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
  }
  
  svg {
    transition: transform var(--transition-base);
  }
  
  &:hover svg {
    transform: translateY(2px);
  }
}

.hero-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2xl);
  padding: var(--space-xl);
  background: var(--bg-secondary);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-lg);
  
  @media (max-width: 768px) {
    flex-direction: column;
    gap: var(--space-lg);
  }
}

.stat-item {
  text-align: center;
  
  .stat-value {
    font-family: var(--font-display);
    font-size: 2rem;
    font-weight: 800;
    background: var(--bg-gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
    margin-bottom: var(--space-xs);
  }
  
  .stat-label {
    font-size: 0.875rem;
    color: var(--text-tertiary);
  }
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: var(--border-color);
  
  @media (max-width: 768px) {
    width: 40px;
    height: 1px;
  }
}

.floating-elements {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  
  @media (max-width: 768px) {
    display: none;
  }
}

.float-card {
  position: absolute;
  background: var(--bg-secondary);
  padding: var(--space-lg);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  display: flex;
  align-items: center;
  gap: var(--space-md);
  
  &.card-1 {
    top: 15%;
    left: 10%;
  }
  
  &.card-2 {
    top: 30%;
    right: 10%;
  }
  
  &.card-3 {
    bottom: 20%;
    left: 15%;
  }
}

.float-icon {
  font-size: 2rem;
}

.float-text {
  font-family: var(--font-display);
  font-weight: 600;
  color: var(--text-primary);
}

/* Features Section */
.features {
  padding: var(--space-3xl) var(--space-xl);
  background: var(--bg-secondary);
  
  @media (max-width: 768px) {
    padding: var(--space-2xl) var(--space-lg);
  }
}

.section-header {
  text-align: center;
  margin-bottom: var(--space-3xl);
}

.section-badge {
  display: inline-block;
  padding: var(--space-sm) var(--space-lg);
  background: var(--bg-gradient-primary);
  color: var(--text-inverse);
  border-radius: var(--radius-full);
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 0.875rem;
  margin-bottom: var(--space-lg);
}

.section-title {
  font-family: var(--font-display);
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 800;
  margin-bottom: var(--space-md);
  color: var(--text-primary);
}

.section-subtitle {
  font-size: 1.25rem;
  color: var(--text-secondary);
  max-width: 600px;
  margin: 0 auto;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--space-xl);
  max-width: 1200px;
  margin: 0 auto;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: var(--space-lg);
  }
}

.feature-card {
  padding: var(--space-2xl);
  background: var(--bg-primary);
  border-radius: var(--radius-2xl);
  border: 2px solid var(--border-color-light);
  transition: all var(--transition-base);
  
  &:hover {
    transform: translateY(-8px);
    box-shadow: var(--shadow-xl);
    border-color: transparent;
  }
}

.feature-icon-wrapper {
  margin-bottom: var(--space-lg);
}

.feature-icon {
  width: 80px;
  height: 80px;
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  box-shadow: var(--shadow-md);
}

.feature-title {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: var(--space-md);
  color: var(--text-primary);
}

.feature-description {
  color: var(--text-secondary);
  line-height: 1.6;
}

/* How it works */
.how-it-works {
  padding: var(--space-3xl) var(--space-xl);
  background: var(--bg-primary);
  
  @media (max-width: 768px) {
    padding: var(--space-2xl) var(--space-lg);
  }
}

.steps-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xl);
  max-width: 1200px;
  margin: 0 auto;
  
  @media (max-width: 768px) {
    flex-direction: column;
    gap: var(--space-2xl);
  }
}

.step {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.step-number {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 40px;
  background: var(--bg-gradient-primary);
  color: var(--text-inverse);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-weight: 800;
  font-size: 1.25rem;
  box-shadow: var(--shadow-colored);
}

.step-content {
  background: var(--bg-secondary);
  padding: var(--space-2xl);
  border-radius: var(--radius-2xl);
  text-align: center;
  box-shadow: var(--shadow-md);
  transition: all var(--transition-base);
  width: 100%;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
  }
}

.step-icon {
  font-size: 3rem;
  margin-bottom: var(--space-lg);
}

.step-title {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: var(--space-md);
  color: var(--text-primary);
}

.step-description {
  color: var(--text-secondary);
}

.step-arrow {
  font-size: 2rem;
  color: var(--text-tertiary);
  margin: 0 var(--space-lg);
  
  @media (max-width: 768px) {
    transform: rotate(90deg);
    margin: var(--space-lg) 0;
  }
}

/* CTA Section */
.cta-section {
  position: relative;
  padding: var(--space-3xl) var(--space-xl);
  background: var(--bg-gradient-hero);
  overflow: hidden;
  
  @media (max-width: 768px) {
    padding: var(--space-2xl) var(--space-lg);
  }
}

.cta-content {
  position: relative;
  z-index: 1;
  text-align: center;
  max-width: 700px;
  margin: 0 auto;
}

.cta-title {
  font-family: var(--font-display);
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 800;
  color: var(--text-inverse);
  margin-bottom: var(--space-lg);
}

.cta-subtitle {
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: var(--space-2xl);
}

.cta-button-large {
  padding: var(--space-xl) var(--space-3xl);
  font-size: 1.25rem;
  font-weight: 700;
  background: var(--bg-secondary);
  color: var(--primary);
  border: none;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  height: auto;
  
  &:hover {
    background: var(--bg-secondary);
    transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  }
  
  .button-content {
    display: flex;
    align-items: center;
    gap: var(--space-md);
  }
  
  .button-icon {
    transition: transform var(--transition-base);
  }
  
  &:hover .button-icon {
    transform: translateX(4px);
  }
}

.cta-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  
  .decoration-circle {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);
    
    &.circle-1 {
      width: 300px;
      height: 300px;
      top: -100px;
      left: -100px;
    }
    
    &.circle-2 {
      width: 200px;
      height: 200px;
      bottom: -50px;
      right: -50px;
    }
    
    &.circle-3 {
      width: 150px;
      height: 150px;
      top: 50%;
      right: 10%;
    }
  }
}
</style>
