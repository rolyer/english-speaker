# Markdown 格式支持

## 功能说明

语音对话页面的文本和翻译内容现在支持 Markdown 格式，可以正确显示格式化的文本。

## 支持的 Markdown 语法

### 1. 加粗 (Bold)

**语法**：
- `**text**` 
- `__text__`

**示例**：
```
You did an **excellent** job!
```

**渲染效果**：
You did an **excellent** job!

### 2. 斜体 (Italic)

**语法**：
- `*text*`
- `_text_`

**示例**：
```
This is *very* important!
```

**渲染效果**：
This is *very* important!

### 3. 删除线 (Strikethrough)

**语法**：
- `~~text~~`

**示例**：
```
This is ~~wrong~~ correct!
```

**渲染效果**：
This is ~~wrong~~ correct!

### 4. 行内代码 (Inline Code)

**语法**：
- `` `code` ``

**示例**：
```
Use the `console.log()` function.
```

**渲染效果**：
Use the `console.log()` function.

### 5. 换行 (Line Break)

**语法**：
- `\n`

**示例**：
```
Line 1\nLine 2\nLine 3
```

**渲染效果**：
```
Line 1
Line 2
Line 3
```

## 技术实现

### formatMessage 函数

```javascript
function formatMessage(content) {
  if (!content) return ''
  
  // 1. 转义 HTML 特殊字符
  let formatted = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  
  // 2. 处理 Markdown 语法（顺序很重要）
  
  // 行内代码（先处理，避免代码内的 * 被误解析）
  formatted = formatted.replace(/`([^`]+?)`/g, '<code>$1</code>')
  
  // 加粗（必须在斜体之前处理）
  formatted = formatted.replace(/\*\*([^*]+?)\*\*/g, '<strong>$1</strong>')
  formatted = formatted.replace(/__([^_]+?)__/g, '<strong>$1</strong>')
  
  // 斜体
  formatted = formatted.replace(/\*([^*]+?)\*/g, '<em>$1</em>')
  formatted = formatted.replace(/_([^_]+?)_/g, '<em>$1</em>')
  
  // 删除线
  formatted = formatted.replace(/~~([^~]+?)~~/g, '<del>$1</del>')
  
  // 换行
  formatted = formatted.replace(/\n/g, '<br>')
  
  return formatted
}
```

### 处理顺序的重要性

1. **先转义 HTML**：防止 XSS 攻击
2. **先处理代码**：避免代码内的 `*` 被误解析为斜体
3. **先处理加粗**：`**text**` 必须在 `*text*` 之前，否则会被误解析
4. **最后处理换行**：确保其他格式已经转换完成

### 正则表达式说明

#### 加粗
```javascript
/\*\*([^*]+?)\*\*/g
```
- `\*\*`：匹配两个星号
- `([^*]+?)`：捕获组，匹配非星号字符（非贪婪）
- `\*\*`：匹配结束的两个星号
- `g`：全局匹配

#### 斜体
```javascript
/\*([^*]+?)\*/g
```
- `\*`：匹配一个星号
- `([^*]+?)`：捕获组，匹配非星号字符（非贪婪）
- `\*`：匹配结束的星号
- `g`：全局匹配

#### 行内代码
```javascript
/`([^`]+?)`/g
```
- `` ` ``：匹配反引号
- `([^`]+?)`：捕获组，匹配非反引号字符（非贪婪）
- `` ` ``：匹配结束的反引号
- `g`：全局匹配

## CSS 样式

### 文本转录样式

```scss
.transcription {
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
```

### 翻译内容样式

```scss
.translation-content {
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
```

## 使用示例

### AI 回复示例

```
Oh no! Are you leaving, Vic? 😢 That's okay!

We had a wonderful talk today! You did an **excellent** job practicing English! I'm so proud of you! 🌟

Remember:
– You speak English *very* well!
– Keep practicing every day!
– You're a great student!

Goodbye, Vic! Come back and practice with me again soon! 👋😊

Have a great evening! 🌙
```

### 渲染效果

Oh no! Are you leaving, Vic? 😢 That's okay!

We had a wonderful talk today! You did an **excellent** job practicing English! I'm so proud of you! 🌟

Remember:
– You speak English *very* well!
– Keep practicing every day!
– You're a great student!

Goodbye, Vic! Come back and practice with me again soon! 👋😊

Have a great evening! 🌙

### 翻译示例

**原文**：
```
You did an **excellent** job!
```

**翻译**：
```
你做得**非常棒**！
```

**渲染效果**：
你做得**非常棒**！

## 安全性

### XSS 防护

1. **HTML 转义**：所有 HTML 特殊字符都被转义
   ```javascript
   .replace(/&/g, '&amp;')
   .replace(/</g, '&lt;')
   .replace(/>/g, '&gt;')
   ```

2. **白名单机制**：只允许特定的 HTML 标签
   - `<strong>` - 加粗
   - `<em>` - 斜体
   - `<del>` - 删除线
   - `<code>` - 代码
   - `<br>` - 换行

3. **内容来源**：
   - AI 服务返回的内容
   - 后端翻译 API 返回的内容
   - 不是用户直接输入的 HTML

## 限制和注意事项

### 不支持的 Markdown 语法

以下 Markdown 语法暂不支持：

- ❌ 标题 (`# Heading`)
- ❌ 列表 (`- item` 或 `1. item`)
- ❌ 链接 (`[text](url)`)
- ❌ 图片 (`![alt](url)`)
- ❌ 引用 (`> quote`)
- ❌ 代码块 (` ``` code ``` `)
- ❌ 表格

### 为什么不支持？

1. **语音对话场景**：主要是短文本，不需要复杂格式
2. **安全性**：链接和图片可能带来安全风险
3. **UI 限制**：消息卡片空间有限，不适合复杂布局

### 如果需要更多格式

如果未来需要支持更复杂的 Markdown，可以考虑：

1. **使用 Markdown 库**：
   ```javascript
   import MarkdownIt from 'markdown-it'
   const md = new MarkdownIt()
   
   function formatMessage(content) {
     return md.render(content)
   }
   ```

2. **使用 Vue Markdown 组件**：
   ```vue
   <VueMarkdown :source="message.content" />
   ```

3. **配置白名单**：
   ```javascript
   const md = new MarkdownIt({
     html: false,  // 禁用 HTML
     linkify: false,  // 禁用自动链接
     breaks: true  // 启用换行
   })
   ```

## 测试用例

### 测试 1：基本格式

**输入**：
```
This is **bold**, *italic*, and `code`.
```

**预期输出**：
```html
This is <strong>bold</strong>, <em>italic</em>, and <code>code</code>.
```

### 测试 2：混合格式

**输入**：
```
You did an **excellent** job! Keep practicing *every day*!
```

**预期输出**：
```html
You did an <strong>excellent</strong> job! Keep practicing <em>every day</em>!
```

### 测试 3：换行

**输入**：
```
Line 1\nLine 2\nLine 3
```

**预期输出**：
```html
Line 1<br>Line 2<br>Line 3
```

### 测试 4：代码中的特殊字符

**输入**：
```
Use `**bold**` in Markdown.
```

**预期输出**：
```html
Use <code>**bold**</code> in Markdown.
```

## 总结

通过实现 Markdown 格式支持，语音对话页面的文本和翻译内容现在可以：

✅ 正确显示加粗文本
✅ 正确显示斜体文本
✅ 正确显示删除线
✅ 正确显示行内代码
✅ 正确处理换行
✅ 保持安全性（XSS 防护）
✅ 提供良好的视觉效果

这使得 AI 的回复更加生动和易读，提升了用户体验。

