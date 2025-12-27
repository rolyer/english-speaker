# TTS 音频缓存功能

## 功能概述

为了节省 TTS API 调用和提高响应速度，实现了双层音频缓存机制：
1. **后端文件缓存**：将生成的音频文件保存到服务器磁盘
2. **前端内存缓存**：在浏览器中缓存音频 Blob 对象

## 工作原理

### 缓存流程

```
用户请求播放文本
    ↓
前端检查浏览器缓存
    ↓
    ├─ 命中 → 直接播放
    ↓
    └─ 未命中 → 请求后端
            ↓
        后端检查文件缓存
            ↓
            ├─ 命中 → 返回缓存文件
            ↓
            └─ 未命中 → 调用 TTS API
                    ↓
                生成音频
                    ↓
                保存到后端缓存
                    ↓
                返回音频数据
                    ↓
            前端保存到浏览器缓存
                    ↓
                播放音频
```

### 缓存键生成

使用 MD5 哈希生成唯一的缓存键，包含以下参数：
- 文本内容（已清理 emoji）
- 语言代码（如 `en-US`）
- 语音名称（如 `en-US-AriaNeural`）
- 语速（如 `+0%`）
- 音调（如 `+0Hz`）

**示例**：
```python
content = "Hello, how are you?|en-US|en-US-AriaNeural||"
hash = md5(content) = "a1b2c3d4e5f6..."
cache_file = "audio_cache/a1b2c3d4e5f6.mp3"
```

## 后端实现

### 1. 缓存目录

**位置**：`backend/audio_cache/`
**格式**：`{hash}.mp3`

### 2. 核心功能

**`generate_audio_hash()`**
```python
def generate_audio_hash(text, language, voice, rate, pitch) -> str:
    """生成音频文件的哈希值"""
    content = f"{text}|{language}|{voice or ''}|{rate or ''}|{pitch or ''}"
    return hashlib.md5(content.encode('utf-8')).hexdigest()
```

**`get_cached_audio()`**
```python
def get_cached_audio(audio_hash: str) -> Optional[bytes]:
    """从缓存获取音频数据"""
    cache_path = self.get_cache_path(audio_hash)
    if cache_path.exists():
        with open(cache_path, 'rb') as f:
            return f.read()
    return None
```

**`save_to_cache()`**
```python
def save_to_cache(audio_hash: str, audio_data: bytes) -> bool:
    """保存音频到缓存"""
    cache_path = self.get_cache_path(audio_hash)
    with open(cache_path, 'wb') as f:
        f.write(audio_data)
    return True
```

**`synthesize_speech()` 改进**
```python
async def synthesize_speech(text, language, voice, rate, pitch, use_cache=True):
    # 生成哈希
    audio_hash = generate_audio_hash(text, language, voice, rate, pitch)
    
    # 检查缓存
    if use_cache:
        cached_audio = self.get_cached_audio(audio_hash)
        if cached_audio:
            return cached_audio  # 直接返回缓存
    
    # 生成新音频
    audio_data = await generate_audio(...)
    
    # 保存到缓存
    if use_cache:
        self.save_to_cache(audio_hash, audio_data)
    
    return audio_data
```

### 3. 缓存管理 API

**获取缓存统计**
```
GET /api/tts/cache/stats
```
返回：
```json
{
  "count": 150,
  "total_size": 15728640,
  "total_size_mb": 15.0,
  "cache_dir": "./audio_cache"
}
```

**清理缓存**
```
DELETE /api/tts/cache?max_age_days=7
```
参数：
- `max_age_days`：删除超过指定天数的文件（可选）
- 不提供参数则删除所有缓存

返回：
```json
{
  "success": true,
  "deleted_count": 50,
  "message": "成功清理 50 个缓存文件"
}
```

## 前端实现

### 1. 浏览器缓存

使用 JavaScript `Map` 对象存储音频 Blob：

```javascript
// 缓存存储
const audioCache = new Map()

// 生成缓存键
function getCacheKey(text, language, rate, pitch) {
  return `${text}|${language}|${rate || '1.0'}|${pitch || '1.0'}`
}
```

### 2. 播放逻辑

```javascript
async function play() {
  const cacheKey = getCacheKey(props.text, props.language, props.rate, props.pitch)
  
  let audioBlob
  
  // 检查浏览器缓存
  if (audioCache.has(cacheKey)) {
    audioBlob = audioCache.get(cacheKey)
    console.log('从浏览器缓存加载音频')
  } else {
    // 请求后端 API
    const response = await axios.post('/api/tts/synthesize', {...})
    audioBlob = response.data
    
    // 保存到缓存
    audioCache.set(cacheKey, audioBlob)
    
    // 限制缓存大小（最多 50 个）
    if (audioCache.size > 50) {
      const firstKey = audioCache.keys().next().value
      audioCache.delete(firstKey)
    }
  }
  
  // 创建音频 URL 并播放
  audioUrl = URL.createObjectURL(audioBlob)
  audio = new Audio(audioUrl)
  await audio.play()
}
```

### 3. 缓存限制

- **最大数量**：50 个音频
- **清理策略**：FIFO（先进先出）
- **生命周期**：页面刷新后清空

## 性能优化

### 命中率提升

**相同文本的重复播放**
- 第一次：调用 TTS API（~2-3秒）
- 第二次：从后端缓存加载（~100-200ms）
- 第三次：从浏览器缓存加载（~10ms）

**常用短语**
- "Hello"、"How are you?" 等常用短语
- 只需生成一次，后续直接使用缓存
- 大幅减少 API 调用

### 资源节省

**API 调用减少**
- 修复前：每次播放都调用 API
- 修复后：相同内容只调用一次

**网络流量节省**
- 浏览器缓存命中：0 网络请求
- 后端缓存命中：只传输音频数据，无 TTS 计算

**响应速度**
- TTS 生成：2-3 秒
- 后端缓存：100-200 毫秒
- 浏览器缓存：10 毫秒以内

## 缓存管理

### 自动清理

可以设置定时任务清理旧缓存：

```python
# 清理 7 天前的缓存
tts_service.clear_cache(max_age_days=7)
```

### 手动清理

通过 API 手动清理：

```bash
# 清理所有缓存
curl -X DELETE http://localhost:8000/api/tts/cache \
  -H "Authorization: Bearer {token}"

# 清理 30 天前的缓存
curl -X DELETE "http://localhost:8000/api/tts/cache?max_age_days=30" \
  -H "Authorization: Bearer {token}"
```

### 查看统计

```bash
curl http://localhost:8000/api/tts/cache/stats \
  -H "Authorization: Bearer {token}"
```

## 配置选项

### 后端配置

**缓存目录**
```python
# backend/app/services/tts_service.py
AUDIO_CACHE_DIR = Path("./audio_cache")
```

**禁用缓存**
```python
# 在调用时禁用缓存
audio_data = await tts_service.synthesize_speech(
    text="Hello",
    use_cache=False  # 不使用缓存
)
```

### 前端配置

**缓存大小限制**
```javascript
// frontend/src/components/AudioPlayer.vue
if (audioCache.size > 50) {  // 修改此数字调整缓存大小
  const firstKey = audioCache.keys().next().value
  audioCache.delete(firstKey)
}
```

## 注意事项

### 1. 磁盘空间

- 每个音频文件约 50-200 KB
- 1000 个缓存文件约 50-200 MB
- 建议定期清理旧缓存

### 2. 缓存一致性

- 相同参数生成相同哈希
- 参数变化会生成新缓存
- emoji 过滤确保文本一致性

### 3. 并发安全

- 后端文件操作是线程安全的
- 前端 Map 操作在单线程中执行
- 无需额外的锁机制

### 4. 错误处理

- 缓存读取失败：回退到生成新音频
- 缓存写入失败：不影响音频返回
- 缓存目录不存在：自动创建

## 测试建议

### 测试场景 1：首次播放
1. 清空所有缓存
2. 播放一段文本
3. 观察 TTS API 调用
4. **预期**：调用 TTS API，保存到缓存

### 测试场景 2：重复播放
1. 再次播放相同文本
2. 观察网络请求
3. **预期**：从浏览器缓存加载，无网络请求

### 测试场景 3：页面刷新
1. 刷新页面
2. 播放之前的文本
3. **预期**：从后端缓存加载，快速返回

### 测试场景 4：不同参数
1. 播放相同文本，不同语速
2. 观察缓存行为
3. **预期**：生成新缓存文件

### 测试场景 5：缓存清理
1. 调用清理 API
2. 再次播放
3. **预期**：重新生成音频

## 监控建议

### 缓存命中率

```python
# 添加统计
cache_hits = 0
cache_misses = 0

def get_cached_audio(audio_hash):
    global cache_hits, cache_misses
    if cache_exists:
        cache_hits += 1
        return cached_audio
    cache_misses += 1
    return None

# 命中率 = cache_hits / (cache_hits + cache_misses)
```

### 磁盘使用

```bash
# 查看缓存目录大小
du -sh backend/audio_cache/

# 查看文件数量
ls backend/audio_cache/ | wc -l
```

### API 调用统计

在日志中记录：
- TTS API 调用次数
- 缓存命中次数
- 平均响应时间

## 相关文件

- `backend/app/services/tts_service.py` - TTS 服务（缓存逻辑）
- `backend/app/api/tts.py` - TTS API 端点
- `frontend/src/components/AudioPlayer.vue` - 音频播放组件（前端缓存）
- `.gitignore` - 忽略缓存目录

## 未来改进

1. **持久化前端缓存**
   - 使用 IndexedDB 替代 Map
   - 支持跨页面缓存
   - 更大的存储空间

2. **智能缓存预热**
   - 预先生成常用短语
   - 后台异步生成
   - 提高首次访问速度

3. **分布式缓存**
   - 使用 Redis 存储音频
   - 支持多服务器共享
   - 更快的访问速度

4. **缓存压缩**
   - 压缩音频文件
   - 减少磁盘占用
   - 加快传输速度

5. **缓存预加载**
   - 分析用户对话模式
   - 预测可能的回复
   - 提前生成音频

