# TTS 重复调用问题修复

## 问题描述

在语音模式下对话几轮后，录音发送后（`/api/chat/stream` 请求成功），接口 `/api/tts/synthesize` 会被不停地调用（或者多次调用）。

## 问题原因

### 1. **ref 引用问题**
在 `VoiceConversation.vue` 中，所有的 `AudioPlayer` 组件使用了相同的 ref：
```vue
<AudioPlayer
  v-if="message.role === 'assistant'"
  :text="message.content"
  :auto-play="voiceMode && message.role === 'assistant'"
  ref="audioPlayerRef"  <!-- 问题：所有组件共享同一个ref -->
/>
```

这导致 Vue 无法正确管理多个组件实例。

### 2. **自动播放逻辑问题**
原来的自动播放条件是：
```vue
:auto-play="voiceMode && message.role === 'assistant'"
```

这意味着**所有历史 AI 消息**都会尝试自动播放，而不仅仅是最新的消息。

### 3. **watch 重复触发**
在 `AudioPlayer.vue` 中，`watch(() => props.text)` 监听文本变化。在流式响应中，文本会不断更新，导致：
- 每次文本更新都触发 watch
- 没有防抖机制
- 没有记录上次播放的文本，可能重复播放相同内容

### 4. **流式响应中的多次触发**
在流式聊天中，AI 的回复是逐字符追加的：
```
"Hello" -> "Hello!" -> "Hello! How" -> "Hello! How are" -> ...
```

每次内容更新都会触发 watch，导致多次调用 TTS API。

## 修复方案

### 1. 移除 ref 引用
**文件：`VoiceConversation.vue` 和 `Conversation.vue`**

移除所有 `AudioPlayer` 组件上的 `ref="audioPlayerRef"`：
```vue
<AudioPlayer
  v-if="message.role === 'assistant'"
  :text="message.content"
  :auto-play="voiceMode && isLatestAssistantMessage(index)"
  <!-- 移除了 ref -->
/>
```

### 2. 只自动播放最新消息
**文件：`VoiceConversation.vue`**

添加 `isLatestAssistantMessage()` 函数来判断是否是最新的 AI 消息：
```javascript
function isLatestAssistantMessage(index) {
  // 从当前索引往后查找，如果没有其他assistant消息，则这是最新的
  for (let i = index + 1; i < chatStore.messages.length; i++) {
    if (chatStore.messages[i].role === 'assistant') {
      return false
    }
  }
  return true
}
```

更新自动播放条件：
```vue
:auto-play="voiceMode && isLatestAssistantMessage(index)"
```

### 3. 改进 watch 逻辑，添加防抖和去重
**文件：`AudioPlayer.vue`**

添加防抖定时器和文本记录：
```javascript
// 用于防抖的定时器
let autoPlayTimer = null
// 记录上次自动播放的文本，避免重复播放
let lastAutoPlayText = ''

watch(() => props.text, (newText, oldText) => {
  // 清除之前的定时器
  if (autoPlayTimer) {
    clearTimeout(autoPlayTimer)
    autoPlayTimer = null
  }
  
  // 如果文本变化且之前正在播放，先停止
  if (oldText && isPlaying.value) {
    stop()
  }
  
  // 只有当文本真正改变、不为空、且与上次播放的文本不同时才自动播放
  if (newText && newText !== oldText && props.autoPlay && newText !== lastAutoPlayText) {
    // 延迟播放，确保DOM已更新，并且避免在流式响应中多次触发
    autoPlayTimer = setTimeout(() => {
      // 再次检查，因为可能在延迟期间用户已经手动播放或文本已改变
      if (props.autoPlay && !isPlaying.value && props.text === newText) {
        lastAutoPlayText = newText
        play()
      }
      autoPlayTimer = null
    }, 500) // 增加延迟时间，等待流式响应完成
  }
}, { immediate: false })
```

### 4. 清理定时器
在组件卸载时清理定时器：
```javascript
onUnmounted(() => {
  // 清除定时器
  if (autoPlayTimer) {
    clearTimeout(autoPlayTimer)
    autoPlayTimer = null
  }
  stop()
  cleanup()
})
```

## 修复效果

### 修复前
- ❌ 每个历史 AI 消息都尝试自动播放
- ❌ 流式响应中每次文本更新都触发 TTS 调用
- ❌ 同一文本可能被播放多次
- ❌ TTS API 被频繁调用，浪费资源

### 修复后
- ✅ 只有最新的 AI 消息会自动播放
- ✅ 流式响应完成后才触发一次 TTS 调用
- ✅ 相同文本不会重复播放
- ✅ 防抖机制避免频繁调用
- ✅ 正确的资源清理

## 技术细节

### 防抖机制
- **延迟时间**：500ms
- **目的**：等待流式响应完成，避免中途触发
- **实现**：使用 `setTimeout` 和 `clearTimeout`

### 去重机制
- **记录上次播放的文本**：`lastAutoPlayText`
- **比较逻辑**：`newText !== lastAutoPlayText`
- **更新时机**：播放开始时更新记录

### 条件检查
播放前进行多重检查：
1. 文本不为空
2. 文本与上次不同
3. `autoPlay` 为 true
4. 当前没有正在播放
5. 文本没有再次改变

### 资源管理
- 组件卸载时清理定时器
- 停止播放时清理音频资源
- 释放 Blob URL

## 测试建议

### 测试场景 1：单次对话
1. 进入语音模式
2. 发送一条消息
3. 观察 Network 面板
4. **预期**：TTS API 只被调用一次

### 测试场景 2：多轮对话
1. 进入语音模式
2. 连续发送 3-5 条消息
3. 观察每次 AI 回复后的 TTS 调用
4. **预期**：每次回复只调用一次 TTS API

### 测试场景 3：快速连续发送
1. 进入语音模式
2. 快速连续发送多条消息（不等待回复完成）
3. 观察 TTS 调用情况
4. **预期**：每个回复只播放一次，不会重复

### 测试场景 4：切换模式
1. 在语音模式下对话
2. 切换到文本模式
3. 再切换回语音模式
4. 继续对话
5. **预期**：不会播放历史消息，只播放新消息

### 测试场景 5：页面刷新
1. 在语音模式下对话几轮
2. 刷新页面
3. 重新进入语音模式
4. **预期**：不会自动播放历史消息

## 性能优化

### 减少 API 调用
- 修复前：可能每秒调用多次 TTS API
- 修复后：每个完整回复只调用一次

### 减少网络流量
- 避免重复下载相同的音频数据
- 及时释放 Blob URL

### 改善用户体验
- 避免多个音频同时播放
- 减少不必要的等待时间
- 更流畅的语音交互

## 相关文件

- `frontend/src/views/VoiceConversation.vue` - 语音对话页面
- `frontend/src/views/Conversation.vue` - 文本对话页面
- `frontend/src/components/AudioPlayer.vue` - 音频播放组件
- `backend/app/api/tts.py` - TTS API 端点
- `backend/app/services/tts_service.py` - TTS 服务

## 注意事项

1. **延迟时间调整**
   - 当前设置为 500ms
   - 如果网络较慢，可能需要增加
   - 如果响应很快，可以适当减少

2. **文本比较**
   - 使用严格相等 `===` 比较
   - 不进行内容清理或格式化
   - 确保完整文本匹配

3. **组件生命周期**
   - 确保在卸载时清理所有资源
   - 避免内存泄漏
   - 正确处理异步操作

4. **错误处理**
   - TTS API 调用失败时的处理
   - 音频播放失败时的处理
   - 网络中断时的处理

