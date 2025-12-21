<template>
  <div class="pronunciation-score">
    <div v-if="score !== null" class="score-display">
      <div class="score-circle">
        <div class="score-value">{{ score }}</div>
        <div class="score-label">分</div>
      </div>
      
      <div class="score-stars">
        <el-icon
          v-for="i in 5"
          :key="i"
          :class="['star', { filled: i <= starCount }]"
        >
          <StarFilled v-if="i <= starCount" />
          <Star v-else />
        </el-icon>
      </div>
      
      <div class="score-level">
        <el-tag :type="levelType">{{ levelText }}</el-tag>
      </div>
    </div>
    
    <div v-if="feedback && feedback.length > 0" class="feedback">
      <h4>改进建议：</h4>
      <ul>
        <li v-for="(item, index) in feedback" :key="index">{{ item }}</li>
      </ul>
    </div>
    
    <div v-if="details" class="details">
      <el-collapse>
        <el-collapse-item title="详细评分" name="details">
          <div class="detail-item">
            <span>准确度：</span>
            <el-progress :percentage="details.accuracy || 0" />
          </div>
          <div class="detail-item">
            <span>流利度：</span>
            <el-progress :percentage="details.fluency || 0" />
          </div>
          <div class="detail-item">
            <span>完整性：</span>
            <el-progress :percentage="details.completeness || 0" />
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { StarFilled, Star } from '@element-plus/icons-vue'

const props = defineProps({
  score: {
    type: Number,
    default: null
  },
  feedback: {
    type: Array,
    default: () => []
  },
  details: {
    type: Object,
    default: null
  }
})

const starCount = computed(() => {
  if (props.score === null) return 0
  return Math.round((props.score / 100) * 5)
})

const levelText = computed(() => {
  if (props.score === null) return '未评分'
  if (props.score >= 90) return '优秀'
  if (props.score >= 80) return '良好'
  if (props.score >= 70) return '中等'
  if (props.score >= 60) return '及格'
  return '需改进'
})

const levelType = computed(() => {
  if (props.score === null) return 'info'
  if (props.score >= 90) return 'success'
  if (props.score >= 80) return 'success'
  if (props.score >= 70) return 'warning'
  if (props.score >= 60) return 'warning'
  return 'danger'
})
</script>

<style lang="scss" scoped>
.pronunciation-score {
  padding: 16px;
  background: var(--bg-light);
  border-radius: 12px;
  margin-top: 12px;
}

.score-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.score-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  
  .score-value {
    font-size: 2rem;
    line-height: 1;
  }
  
  .score-label {
    font-size: 0.9rem;
    opacity: 0.9;
  }
}

.score-stars {
  display: flex;
  gap: 4px;
  
  .star {
    font-size: 24px;
    color: #ddd;
    
    &.filled {
      color: #ffd700;
    }
  }
}

.score-level {
  margin-top: 8px;
}

.feedback {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
  
  h4 {
    margin: 0 0 12px 0;
    color: var(--text-color);
    font-size: 1rem;
  }
  
  ul {
    margin: 0;
    padding-left: 20px;
    
    li {
      margin-bottom: 8px;
      color: var(--text-light);
      line-height: 1.6;
    }
  }
}

.details {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.detail-item {
  margin-bottom: 12px;
  
  span {
    display: inline-block;
    width: 80px;
    color: var(--text-light);
    font-size: 0.9rem;
  }
  
  .el-progress {
    display: inline-block;
    width: calc(100% - 100px);
    vertical-align: middle;
  }
}
</style>

