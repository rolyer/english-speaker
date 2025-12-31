# 自动播放音频调试指南

## 🔧 修复内容

### 1. 修复 VoiceConversation 页面默认语音模式

**问题**：`voiceMode` 默认值为 `false`，导致 `auto-play` 条件永远不满足

**修复**：
```javascript
// 修改前
const voiceMode = ref(false)

// 修改后
const voiceMode = ref(true) // 语音对话页面默认开启语音模式
```

### 2. 添加详细的调试日志

在以下位置添加了 console.log：

**AudioPlayer.vue**：
- text 变化时的详细信息
- 自动播放条件检查
- 定时器设置和执行
- 播放成功/失败的原因

**VoiceConversation.vue**：
- 最新消息判断逻辑
- voiceMode 状态
- autoPlay 计算结果

## 🧪 测试步骤

### 1. 启动应用

```bash
# 终端1：启动后端
cd /Users/qinghe/Develop/Ai/speaker/backend
source .venv/bin/activate
./start.sh

# 终端2：启动前端
cd /Users/qinghe/Develop/Ai/speaker/frontend
npm run dev
```

### 2. 测试自动播放

1. 打开浏览器开发者工具（F12）
2. 切换到 Console 标签
3. 访问 http://localhost:3000/voice
4. 点击录音按钮，说一句英文（如 "Hello"）
5. 观察 Console 输出

### 3. 预期的日志输出

```
[VoiceConversation] 最新AI消息: {
  index: 1,
  contentLength: 45,
  voiceMode: true,
  autoPlay: true
}

[AudioPlayer] text changed: {
  newTextLength: 45,
  oldTextLength: 0,
  autoPlay: true,
  isPlaying: false,
  lastAutoPlayText: undefined
}

[AudioPlayer] 设置自动播放定时器，800ms后执行

// 800ms 后...

[AudioPlayer] ✅ 自动播放音频: Hello! How can I help you today?...
从浏览器缓存加载音频
```

### 4. 如果没有自动播放，检查日志

#### 情况1：autoPlay 为 false
```
[AudioPlayer] 不满足自动播放条件: {
  hasNewText: true,
  textChanged: true,
  autoPlay: false,  // ❌ 问题在这里
  notLastPlayed: true
}
```
**原因**：voiceMode 未正确设置
**解决**：检查 `voiceMode.value` 是否为 `true`

#### 情况2：isLatestAssistantMessage 返回 false
```
// 没有看到 "[VoiceConversation] 最新AI消息" 日志
```
**原因**：消息索引判断有问题
**解决**：检查消息数组和索引

#### 情况3：文本还在变化
```
[AudioPlayer] ❌ 取消自动播放: {
  autoPlay: true,
  isPlaying: false,
  textChanged: true  // ❌ 文本在800ms内又变化了
}
```
**原因**：流式响应还未完成
**解决**：增加延迟时间（当前是800ms）

#### 情况4：已经播放过
```
[AudioPlayer] 不满足自动播放条件: {
  hasNewText: true,
  textChanged: true,
  autoPlay: true,
  notLastPlayed: false  // ❌ 已经播放过这段文本
}
```
**原因**：去重机制生效
**解决**：这是正常行为，避免重复播放

## 🔍 关键检查点

### 1. VoiceConversation.vue

```vue
<!-- 检查 voiceMode 的初始值 -->
const voiceMode = ref(true) // ✅ 必须是 true

<!-- 检查 AudioPlayer 的 auto-play 绑定 -->
<AudioPlayer
  v-if="message.role === 'assistant'"
  :text="message.content"
  :auto-play="voiceMode && isLatestAssistantMessage(index)"
/>
```

### 2. AudioPlayer.vue

```javascript
// 检查 props 定义
const props = defineProps({
  autoPlay: {
    type: Boolean,
    default: false
  }
})

// 检查 watch 逻辑
watch(() => props.text, (newText, oldText) => {
  if (newText && newText !== oldText && props.autoPlay && newText !== lastAutoPlayText) {
    // 应该进入这里
  }
})
```

### 3. 浏览器控制台

打开 Vue DevTools，检查：
- VoiceConversation 组件的 `voiceMode` 状态
- AudioPlayer 组件的 `autoPlay` prop
- messages 数组的内容

## 🐛 常见问题

### 问题1：没有任何日志输出

**可能原因**：
- 浏览器缓存未清除
- 代码未重新编译
- 控制台被清空

**解决方法**：
```bash
# 停止前端服务（Ctrl+C）
# 清除缓存并重启
rm -rf node_modules/.vite
npm run dev
```

### 问题2：autoPlay 始终为 false

**可能原因**：
- voiceMode 未设置为 true
- isLatestAssistantMessage 返回 false

**解决方法**：
在 VoiceConversation.vue 的 template 中临时添加：
```vue
<div style="position: fixed; top: 10px; right: 10px; background: white; padding: 10px; z-index: 9999;">
  voiceMode: {{ voiceMode }}
</div>
```

### 问题3：定时器设置了但没有执行

**可能原因**：
- 文本在 800ms 内又变化了
- 组件被卸载了

**解决方法**：
增加延迟时间到 1200ms 试试：
```javascript
}, 1200) // 从 800 增加到 1200
```

### 问题4：TTS API 调用失败

**可能原因**：
- 网络问题
- Token 过期
- 后端服务未启动

**解决方法**：
检查 Network 标签，查看 `/api/tts/synthesize` 请求的状态

## 📊 性能监控

### 检查 TTS 缓存是否生效

```bash
# 查看缓存目录
ls -lh /Users/qinghe/Develop/Ai/speaker/backend/audio_cache/

# 查看缓存统计
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/tts/cache/stats
```

预期输出：
```json
{
  "total_files": 5,
  "total_size_bytes": 245760,
  "total_size_mb": 0.23
}
```

### 检查浏览器缓存

在 Console 中运行：
```javascript
// 查看 AudioPlayer 组件的缓存
// 需要在 AudioPlayer.vue 中暴露 audioCache
console.log('浏览器缓存数量:', audioCache.size)
```

## ✅ 成功标志

当自动播放正常工作时，你应该看到：

1. **Console 日志**：
   - ✅ `[VoiceConversation] 最新AI消息`
   - ✅ `[AudioPlayer] text changed`
   - ✅ `[AudioPlayer] 设置自动播放定时器`
   - ✅ `[AudioPlayer] ✅ 自动播放音频`
   - ✅ `从浏览器缓存加载音频` 或 API 请求成功

2. **UI 表现**：
   - ✅ AI 回复完成后，播放按钮自动变为"暂停"图标
   - ✅ 显示"正在播放..."文本
   - ✅ 能听到语音

3. **Network 标签**：
   - ✅ 第一次播放：有 `/api/tts/synthesize` 请求
   - ✅ 第二次播放相同文本：没有新的 API 请求（使用缓存）

## 🎯 下一步

如果自动播放仍然不工作，请提供：

1. **完整的 Console 日志**（从发送消息到 AI 回复完成）
2. **Network 标签的截图**（特别是 `/api/chat/stream` 和 `/api/tts/synthesize`）
3. **Vue DevTools 的组件状态截图**
4. **浏览器和操作系统信息**

这将帮助我们进一步诊断问题。

