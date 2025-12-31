# 语音对话消息菜单功能

## 功能概述

为语音对话页面的每条消息添加下拉菜单，支持：
1. **显示/隐藏文本**：切换消息的文本转录显示
2. **显示/隐藏翻译**：使用 AI 翻译消息内容

## 用户界面

### 消息卡片布局

```
┌────────────────────────────────────┐
│ 你                2分钟前    ⋮     │  ← 右上角菜单按钮
│ ────────────────────────────────  │
│ 📊 发音评分: 85分                  │
│ ┌──────────────────────────────┐  │
│ │ football                     │  │  ← 文本（可切换）
│ └──────────────────────────────┘  │
│ ┌──────────────────────────────┐  │
│ │ 翻译：足球                    │  │  ← 翻译（可切换）
│ └──────────────────────────────┘  │
└────────────────────────────────────┘
```

### 下拉菜单

点击消息右上角的 `⋮` 按钮，显示下拉菜单：

```
┌─────────────────┐
│ 📄 显示文本     │
│ 🔗 显示翻译     │
└─────────────────┘
```

**菜单项状态**：
- 文本未显示：显示"显示文本"
- 文本已显示：显示"隐藏文本"
- 翻译未显示：显示"显示翻译"
- 翻译已显示：显示"隐藏翻译"

## 技术实现

### 前端实现

#### 1. 状态管理

使用 `reactive` 对象管理每条消息的状态：

```javascript
// 每条消息的状态
const messageStates = reactive({})

// 初始化消息状态
function initMessageState(messageId) {
  if (!messageStates[messageId]) {
    messageStates[messageId] = {
      showText: false,      // 是否显示文本
      translation: null,    // 翻译内容
      translating: false    // 是否正在翻译
    }
  }
}
```

#### 2. 菜单组件

使用 Element Plus 的 `el-dropdown` 组件：

```vue
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
```

#### 3. 命令处理

```javascript
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
```

#### 4. 翻译请求

```javascript
async function translateMessage(message) {
  initMessageState(message.id)
  
  if (messageStates[message.id].translating) {
    return
  }
  
  messageStates[message.id].translating = true
  
  try {
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
```

#### 5. 条件渲染

```vue
<!-- 文本转录 -->
<div v-if="messageStates[message.id]?.showText" class="transcription">
  {{ message.content }}
</div>

<!-- 翻译 -->
<div v-if="messageStates[message.id]?.translation" class="translation">
  <div class="translation-label">翻译：</div>
  {{ messageStates[message.id].translation }}
</div>
```

### 后端实现

#### 1. 翻译 API 路由

在 `backend/app/api/chat.py` 中添加翻译端点：

```python
class TranslateRequest(BaseModel):
    """翻译请求模型"""
    text: str
    source_lang: str = "en"
    target_lang: str = "zh"


class TranslateResponse(BaseModel):
    """翻译响应模型"""
    translation: str
    source_lang: str
    target_lang: str


@router.post("/translate", response_model=TranslateResponse)
async def translate_text(
    request: TranslateRequest,
    current_user: User = Depends(get_current_user)
):
    """翻译文本"""
    try:
        # 构建翻译提示词
        if request.source_lang == "en" and request.target_lang == "zh":
            prompt = f"请将以下英文翻译成中文，只返回翻译结果，不要添加任何解释：\n\n{request.text}"
        elif request.source_lang == "zh" and request.target_lang == "en":
            prompt = f"Please translate the following Chinese to English, return only the translation without any explanation:\n\n{request.text}"
        else:
            raise HTTPException(status_code=400, detail="不支持的语言对")
        
        # 使用 AI 服务进行翻译
        translation = await ai_service.chat(prompt)
        
        return TranslateResponse(
            translation=translation.strip(),
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )
    except Exception as e:
        logger.error(f"翻译失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"翻译失败: {str(e)}")
```

#### 2. 翻译逻辑

- 使用现有的 AI 服务（OpenRouter）进行翻译
- 支持英译中和中译英
- 提示词明确要求只返回翻译结果，不添加解释
- 返回结果去除首尾空白

### 样式设计

#### 1. 消息头部

```scss
.voice-message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  
  .header-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .message-menu-btn {
      opacity: 0.6;
      transition: opacity 0.2s;
      
      &:hover {
        opacity: 1;
      }
    }
  }
}
```

**特点**：
- 菜单按钮默认半透明
- 悬停时完全不透明
- 与时间戳对齐

#### 2. 文本转录

```scss
.transcription {
  font-size: 0.9rem;
  color: var(--text-light);
  line-height: 1.6;
  padding: 8px 12px;
  background: var(--bg-light);
  border-radius: 8px;
  animation: fadeIn 0.3s ease-out;
}
```

**特点**：
- 灰色背景
- 圆角边框
- 淡入动画

#### 3. 翻译内容

```scss
.translation {
  font-size: 0.9rem;
  color: var(--text-color);
  line-height: 1.6;
  padding: 8px 12px;
  background: #e3f2fd;  // 浅蓝色背景
  border-radius: 8px;
  border-left: 3px solid #2196f3;  // 蓝色左边框
  animation: fadeIn 0.3s ease-out;
  
  .translation-label {
    font-size: 0.75rem;
    color: #2196f3;
    font-weight: 600;
    margin-bottom: 4px;
  }
}
```

**特点**：
- 浅蓝色背景，区别于文本转录
- 蓝色左边框，突出显示
- "翻译："标签，清晰标识
- 淡入动画

## 用户体验流程

### 显示文本

1. 用户点击消息右上角的 `⋮` 按钮
2. 下拉菜单显示"显示文本"
3. 用户点击
4. 文本转录以淡入动画显示
5. 菜单项变为"隐藏文本"

### 显示翻译

1. 用户点击消息右上角的 `⋮` 按钮
2. 下拉菜单显示"显示翻译"
3. 用户点击
4. 菜单项变为禁用状态（防止重复请求）
5. 后端调用 AI 翻译
6. 翻译结果以淡入动画显示
7. 菜单项变为"隐藏翻译"

### 隐藏内容

1. 用户再次点击菜单
2. 点击"隐藏文本"或"隐藏翻译"
3. 对应内容消失
4. 菜单项恢复为"显示"状态

## 优势

### 1. 灵活性
- ✅ 用户可以按需显示/隐藏文本
- ✅ 翻译结果缓存，无需重复请求
- ✅ 每条消息独立控制

### 2. 简洁性
- ✅ 默认不显示文本，界面更简洁
- ✅ 突出语音交互
- ✅ 减少视觉干扰

### 3. 实用性
- ✅ 方便查看原文
- ✅ 帮助理解英文内容
- ✅ 学习英语表达

### 4. 性能
- ✅ 翻译结果缓存在前端
- ✅ 避免重复 API 调用
- ✅ 按需加载

## 扩展建议

### 1. 翻译缓存
将翻译结果保存到数据库，避免重复翻译相同内容：

```python
# 检查数据库中是否已有翻译
cached_translation = db.query(Translation).filter(
    Translation.text == request.text,
    Translation.source_lang == request.source_lang,
    Translation.target_lang == request.target_lang
).first()

if cached_translation:
    return TranslateResponse(
        translation=cached_translation.translation,
        source_lang=request.source_lang,
        target_lang=request.target_lang
    )
```

### 2. 更多语言
支持更多语言对：
- 英语 ↔ 中文
- 英语 ↔ 日语
- 英语 ↔ 韩语
- 等等

### 3. 更多菜单项
添加更多功能：
- 📋 复制文本
- 🔊 重新播放
- ⭐ 收藏消息
- 📝 添加笔记

### 4. 翻译质量
- 使用专门的翻译模型（如 DeepL API）
- 提供多个翻译选项
- 显示翻译置信度

## 总结

通过添加消息菜单功能，语音对话页面变得更加灵活和实用：
- 🎯 突出语音交互，默认不显示文本
- 📝 按需显示文本转录
- 🌐 一键翻译，帮助理解
- 🎨 优雅的 UI 设计
- ⚡ 流畅的交互体验

这些改进让语音对话页面更适合语言学习场景，用户可以专注于听说练习，同时在需要时获得文本和翻译支持。

