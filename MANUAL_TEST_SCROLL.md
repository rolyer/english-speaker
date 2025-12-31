# 手动测试滚动功能

## 步骤 1: 检查容器是否存在

在浏览器控制台中运行：

```javascript
const container = document.querySelector('.messages-container')
console.log('Container found:', container !== null)
console.log('Container:', container)
```

**预期结果：** 应该显示 `Container found: true` 和容器元素

---

## 步骤 2: 检查容器尺寸

```javascript
const container = document.querySelector('.messages-container')
if (container) {
  console.log({
    scrollHeight: container.scrollHeight,
    clientHeight: container.clientHeight,
    scrollTop: container.scrollTop,
    offsetHeight: container.offsetHeight,
    hasScrollbar: container.scrollHeight > container.clientHeight,
    overflowY: window.getComputedStyle(container).overflowY
  })
}
```

**预期结果：** 
- `hasScrollbar` 应该为 `true`
- `overflowY` 应该为 `"auto"` 或 `"scroll"`
- `scrollHeight` 应该大于 `clientHeight`

---

## 步骤 3: 手动绑定滚动事件测试

```javascript
const container = document.querySelector('.messages-container')
if (container) {
  container.addEventListener('scroll', (e) => {
    console.log('Manual scroll event:', {
      scrollTop: e.target.scrollTop,
      scrollHeight: e.target.scrollHeight,
      clientHeight: e.target.clientHeight
    })
  })
  console.log('Manual scroll listener added')
}
```

然后尝试滚动，看是否有输出。

---

## 步骤 4: 检查消息数量

```javascript
const messages = document.querySelectorAll('.message-item')
console.log('Message count:', messages.length)
console.log('Messages container children:', document.querySelector('.messages-list')?.children.length)
```

---

## 步骤 5: 强制添加足够的高度

如果容器没有滚动条，可以临时添加一些高度来测试：

```javascript
const container = document.querySelector('.messages-container')
if (container) {
  // 临时增加内容高度
  const messagesList = container.querySelector('.messages-list')
  if (messagesList) {
    messagesList.style.minHeight = '2000px'
    console.log('Added min-height to messages-list')
  }
}
```

然后再尝试滚动。

---

## 步骤 6: 检查 Vue 组件的 ref

```javascript
// 这个需要在 Vue DevTools 中查看
// 或者通过以下方式检查元素上是否有 Vue 实例
const container = document.querySelector('.messages-container')
console.log('Has __vue__:', '__vue__' in container)
```

---

## 如果以上都正常但还是没有事件

可能是 Vue 的事件绑定有问题。请提供以下信息：

1. 步骤 1-4 的输出结果
2. 浏览器控制台是否有任何错误
3. 页面中是否能看到消息内容

