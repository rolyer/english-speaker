# 语音气泡 UI 更新

## 概述

将语音对话页面的消息展示更新为类似微信/WhatsApp的语音气泡样式，提供更直观的语音消息体验。

## 设计参考

```
┌────────────────────────────────────────────────────┐
│ ...                                 25''  语音气泡  │ 用户头像
│  (左侧菜单)              (小体字显示语音时长)  (点击播放)│
└────────────────────────────────────────────────────┘

      ┌────────────────────────────────────────────────────┐
AI头像 │  语音气泡 10''                                   ...│
      │  (点击播放) (小体字显示语音时长)              (左侧菜单) │
      └────────────────────────────────────────────────────┘
```

## 主要变更

### 1. 消息布局

#### 用户消息（右侧）
```
[菜单按钮] [语音气泡] [用户头像]
```

#### AI 消息（左侧）
```
[AI头像] [语音气泡] [菜单按钮]
```

### 2. 语音气泡组件

#### 视觉元素
- **播放图标**：点击播放/暂停
- **声波动画**：播放时显示动态声波
- **时长显示**：右侧显示语音时长（秒）
- **发音评分**：用户消息右上角显示分数徽章

#### 交互行为
- 点击气泡播放/暂停音频
- 播放时图标变为暂停图标
- 播放时声波动画激活
- 气泡悬停时轻微上浮效果

### 3. 样式特点

#### 用户气泡
- 渐变背景：粉色系 (`var(--primary-color)` → `#ff8fab`)
- 白色文字和图标
- 圆角：20px
- 阴影：0 2px 8px rgba(0, 0, 0, 0.1)

#### AI 气泡
- 白色背景
- 浅灰色边框
- 深色文字和图标
- 圆角：20px
- 阴影：0 2px 8px rgba(0, 0, 0, 0.1)

### 4. 头像样式

#### 用户头像
- 圆形：40px × 40px (移动端 36px)
- 渐变背景：粉色系
- 图标：👤

#### AI 头像
- 圆形：40px × 40px (移动端 36px)
- 渐变背景：紫色系 (`#667eea` → `#764ba2`)
- 图标：🤖

## 技术实现

### 新增功能

#### 1. 音频时长计算

```javascript
function getAudioDuration(message) {
  if (!message.content) return 0
  // 简单估算：英文按单词数，平均每个单词0.5秒
  const words = message.content.split(/\s+/).length
  const duration = Math.max(1, Math.ceil(words * 0.5))
  return Math.min(60, duration) // 最多显示60秒
}
```

**估算规则**：
- 按空格分割计算单词数
- 每个单词约 0.5 秒
- 最小 1 秒，最大 60 秒

#### 2. 播放状态管理

```javascript
const currentPlayingId = ref(null) // 当前正在播放的消息ID
const audioCache = new Map() // 音频缓存

function isPlayingMessage(messageId) {
  return currentPlayingId.value === messageId
}
```

#### 3. 音频播放控制

```javascript
async function playMessageAudio(message) {
  currentPlayingId.value = message.id
  
  // 使用隐藏的 AudioPlayer 组件播放
  const audioPlayer = audioPlayerRefs.value[message.id]
  if (audioPlayer && typeof audioPlayer.play === 'function') {
    await audioPlayer.play()
  }
}

function stopAudio() {
  if (currentPlayingId.value) {
    const audioPlayer = audioPlayerRefs.value[currentPlayingId.value]
    if (audioPlayer && typeof audioPlayer.pause === 'function') {
      audioPlayer.pause()
    }
    currentPlayingId.value = null
  }
}
```

### 组件结构

```vue
<div class="voice-message-row" :class="message.role">
  <!-- 用户消息 -->
  <template v-if="message.role === 'user'">
    <div class="voice-bubble-container">
      <!-- 菜单按钮 -->
      <el-dropdown>...</el-dropdown>
      
      <!-- 语音气泡 -->
      <div class="voice-bubble user-bubble" @click="playUserAudio(message)">
        <el-icon class="play-icon">...</el-icon>
        <div class="sound-wave-mini">...</div>
        <span class="voice-duration">25"</span>
        <div class="score-badge">95</div>
      </div>
      
      <!-- 展开的文本/翻译 -->
      <div class="expanded-content">...</div>
    </div>
    
    <!-- 用户头像 -->
    <div class="message-avatar user-avatar">👤</div>
  </template>
  
  <!-- AI 消息 -->
  <template v-else>
    <div class="message-avatar ai-avatar">🤖</div>
    
    <div class="voice-bubble-container">
      <!-- 隐藏的 AudioPlayer -->
      <AudioPlayer style="display: none;" />
      
      <!-- 语音气泡 -->
      <div class="voice-bubble ai-bubble" @click="playAIAudio(message)">
        <el-icon class="play-icon">...</el-icon>
        <div class="sound-wave-mini">...</div>
        <span class="voice-duration">10"</span>
      </div>
      
      <!-- 菜单按钮 -->
      <el-dropdown>...</el-dropdown>
      
      <!-- 展开的文本/翻译 -->
      <div class="expanded-content">...</div>
    </div>
  </template>
</div>
```

## 动画效果

### 1. 声波动画

```scss
@keyframes soundWaveMini {
  0%, 100% {
    height: 8px;
  }
  50% {
    height: 16px;
  }
}

.sound-wave-mini.active span {
  animation: soundWaveMini 0.8s infinite ease-in-out;
  
  &:nth-child(1) { animation-delay: 0s; }
  &:nth-child(2) { animation-delay: 0.1s; }
  &:nth-child(3) { animation-delay: 0.2s; }
}
```

### 2. 播放图标脉冲

```scss
.play-icon.playing {
  animation: pulse 1.5s infinite;
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
```

### 3. 气泡悬停效果

```scss
.voice-bubble {
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  
  &:active {
    transform: scale(0.98);
  }
}
```

### 4. 消息滑入动画

```scss
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

.voice-message-row {
  animation: slideUp 0.3s ease-out;
}
```

## 响应式设计

### 移动端适配

```scss
@media (max-width: 768px) {
  .message-avatar {
    width: 36px;
    height: 36px;
    font-size: 20px;
  }
  
  .voice-bubble-container {
    max-width: 75%;
  }
}
```

## 功能特性

### 1. 点击播放/暂停

- 点击气泡播放音频
- 再次点击暂停播放
- 播放时显示暂停图标
- 播放时激活声波动画

### 2. 发音评分显示

- 用户消息右上角显示分数徽章
- 绿色背景 (`#4caf50`)
- 白色文字
- 圆角徽章样式

### 3. 展开文本/翻译

- 点击菜单按钮
- 选择"显示文本"或"显示翻译"
- 内容展开在气泡下方
- 支持 Markdown 格式

### 4. 音频时长显示

- 自动估算音频时长
- 显示在气泡右侧
- 格式：`10"` (秒)

## 用户体验改进

### 之前的问题

1. ❌ 消息展示过于复杂，不够直观
2. ❌ 播放按钮不明显
3. ❌ 缺少时长信息
4. ❌ 不像语音消息

### 现在的改进

1. ✅ 语音气泡样式，一目了然
2. ✅ 大图标，点击区域更大
3. ✅ 显示时长，用户心里有数
4. ✅ 声波动画，播放状态清晰
5. ✅ 发音评分徽章，成就感更强

## 兼容性

### 浏览器支持

- ✅ Chrome/Edge (推荐)
- ✅ Safari
- ✅ Firefox
- ✅ 移动端浏览器

### 功能降级

- 如果 AudioPlayer 组件不可用，直接调用 TTS API
- 如果音频播放失败，显示错误提示
- 如果浏览器不支持自动播放，用户手动点击

## 测试建议

### 功能测试

1. **播放控制**
   - [ ] 点击用户气泡播放音频
   - [ ] 点击 AI 气泡播放音频
   - [ ] 播放时再次点击暂停
   - [ ] 播放一条消息时，点击另一条消息切换播放

2. **视觉反馈**
   - [ ] 播放时图标变为暂停图标
   - [ ] 播放时声波动画激活
   - [ ] 气泡悬停时有上浮效果
   - [ ] 点击时有缩放反馈

3. **时长显示**
   - [ ] 短消息显示合理时长
   - [ ] 长消息显示合理时长
   - [ ] 时长不超过 60 秒

4. **发音评分**
   - [ ] 用户消息显示评分徽章
   - [ ] AI 消息不显示评分
   - [ ] 评分位置正确（右上角）

5. **展开功能**
   - [ ] 点击菜单显示文本
   - [ ] 点击菜单显示翻译
   - [ ] 展开内容格式正确
   - [ ] 支持 Markdown 格式

### 响应式测试

1. **桌面端** (>768px)
   - [ ] 头像 40px
   - [ ] 气泡最大宽度 70%
   - [ ] 布局正常

2. **移动端** (≤768px)
   - [ ] 头像 36px
   - [ ] 气泡最大宽度 75%
   - [ ] 触摸操作流畅

## 后续优化建议

### 1. 真实时长

```javascript
// 从 TTS API 获取实际音频时长
async function getActualDuration(message) {
  const response = await axios.post('/api/tts/synthesize', {
    text: message.content,
    language: 'en-US'
  }, {
    responseType: 'blob'
  })
  
  const audioBlob = response.data
  const audioUrl = URL.createObjectURL(audioBlob)
  const audio = new Audio(audioUrl)
  
  return new Promise((resolve) => {
    audio.addEventListener('loadedmetadata', () => {
      resolve(Math.ceil(audio.duration))
      URL.revokeObjectURL(audioUrl)
    })
  })
}
```

### 2. 播放进度

```javascript
// 显示播放进度条
const playProgress = ref(0)

audio.addEventListener('timeupdate', () => {
  playProgress.value = (audio.currentTime / audio.duration) * 100
})
```

### 3. 语音识别可视化

```javascript
// 录音时显示实时波形
const audioContext = new AudioContext()
const analyser = audioContext.createAnalyser()
// ... 实现波形可视化
```

### 4. 缓存优化

```javascript
// 预加载下一条消息的音频
async function preloadNextAudio(currentIndex) {
  const nextMessage = chatStore.messages[currentIndex + 1]
  if (nextMessage && nextMessage.role === 'assistant') {
    // 预加载音频
  }
}
```

## 总结

通过这次更新，语音对话页面的消息展示更加直观和易用：

✅ 语音气泡样式，符合用户习惯
✅ 大图标和点击区域，操作更便捷
✅ 时长显示，信息更完整
✅ 声波动画，状态更清晰
✅ 发音评分徽章，反馈更直观
✅ 响应式设计，适配各种设备

这些改进显著提升了语音对话的用户体验，使其更接近主流即时通讯应用的交互模式。

