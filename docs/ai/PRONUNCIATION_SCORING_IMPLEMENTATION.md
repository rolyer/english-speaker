# 发音评分功能实现文档

## 概述

在 `whisper` 分支上实现了完整的语音消息发音评分链路，包括：
- STT 转写带置信度
- 弱评分占位算法
- 低置信度标记与 UI 反馈
- 评分数据库存储与历史加载
- Dashboard 平均分统计

## 实现内容

### 后端改动

#### 1. STTService 增强 (`backend/app/services/stt_service.py`)
- 新增 `transcribe_with_confidence()` 方法
- 基于 Whisper segments 的 `avg_logprob` 计算置信度（0..1）
- 返回 `{text, confidence, low_confidence, language}`
- 低置信度阈值：`confidence < 0.55`

#### 2. 语音对话合并接口 (`backend/app/api/voice.py`)
- **新接口**: `POST /api/voice/chat/stream`
- **功能**: 一次请求完成 STT → 评分 → 保存用户消息 → 流式 AI 回复
- **弱评分算法**:
  ```python
  score = 60 + 40 * confidence  # 基础分 60-100
  if low_confidence: score = min(score, 75)  # 低置信度封顶
  if len(words) < 2: score = min(score, 70)  # 短句降分
  ```
- **SSE 流格式**:
  - `type: meta` - 用户消息元数据（含评分、置信度）
  - `type: chunk` - AI 回复片段
  - `type: done` - 完成标记
  - `type: error` - 错误信息

#### 3. 历史会话接口增强 (`backend/app/api/chat.py`)
- `GET /api/chat/conversations` 返回消息时包含 `pronunciation_score`
- `GET /api/chat/conversations/{id}` 同样返回 `pronunciation_score`

#### 4. 路由注册 (`backend/app/main.py`)
- 注册 `voice.router`

### 前端改动

#### 1. MediaAudioRecorder 简化 (`frontend/src/components/MediaAudioRecorder.vue`)
- 录音完成后只 emit `{audio: Blob, mime, language}`
- 不再自己调用 `/api/stt/transcribe`
- 由上层组件统一处理

#### 2. VoiceConversation 语音流处理 (`frontend/src/views/VoiceConversation.vue`)
- `handleVoiceResult()` 改为接收 `{audio, mime, language}`
- 调用 `/api/voice/chat/stream` 上传音频
- 解析 SSE 流：
  - 收到 `meta` 时插入用户消息（含 `pronunciation_score`、`stt_low_confidence`）
  - 收到 `chunk` 时更新 AI 消息
  - 收到 `done` 时完成

#### 3. 低置信度 UI 标记
- 徽章使用 `el-tooltip`，低置信度时启用
- Tooltip 内容：*"识别置信度低，本次评分可能不准确"*
- CSS 样式：`.score-badge.low-confidence { background: #9e9e9e; opacity: 0.85; }`

#### 4. chatStore 历史加载 (`frontend/src/stores/chat.js`)
- `loadConversation()` 映射消息时保留 `pronunciation_score`

## 数据库字段

### messages 表
- `pronunciation_score` (Float, nullable) - 发音评分 0-100
- `audio_url` (String, nullable) - 音频文件 URL（当前未使用）

### learning_progress 表
- `average_score` (Float) - 平均发音评分（自动计算）

## 使用方式

### 语音对话流程
1. 用户点击录音按钮开始录音
2. 停止录音后，`MediaAudioRecorder` emit audioBlob
3. `VoiceConversation` 上传音频到 `/api/voice/chat/stream`
4. 后端：
   - Whisper 转写（带置信度）
   - 计算弱评分
   - 保存用户消息（含评分）
   - 流式返回 AI 回复
5. 前端：
   - 显示用户消息（带评分徽章）
   - 低置信度时徽章变灰 + tooltip
   - 流式显示 AI 回复

### 查看评分
- **语音对话页面**: 用户消息右上角显示评分徽章
- **Dashboard**: 显示平均评分（所有有评分的消息平均值）
- **历史会话**: 加载历史时评分徽章正常显示

## 评分说明

### 当前评分算法（弱评分占位）
这是一个基于 STT 置信度的**占位评分**，目的是：
- ✅ 让评分链路跑通（DB、UI、统计）
- ✅ 分数与识别稳定度相关（用户体感一致）
- ✅ 明确标注低置信度（避免误导）

**不是真正的音素级发音评测**，后续可替换为：
- GOP (Goodness of Pronunciation)
- 强制对齐 + 音素后验概率
- 第三方发音评测 API（Azure、讯飞等）

### 评分范围
- **60-100**: 基础分数，和 STT confidence 线性相关
- **≤75**: 低置信度时封顶
- **≤70**: 短句（<2词）时封顶

### 低置信度判定
- `confidence < 0.55` 时标记为低置信度
- UI 上徽章变灰 + tooltip 提示

## 测试建议

### 功能测试
1. 录音并发送语音消息
2. 检查用户消息是否显示评分徽章
3. 检查低置信度时徽章是否变灰
4. 悬停徽章查看 tooltip
5. 刷新页面，检查历史消息评分是否保留
6. 访问 Dashboard，检查平均评分是否显示

### 预期行为
- 清晰发音 → 高分（80-95）+ 绿色徽章
- 模糊/噪音 → 低分（60-75）+ 灰色徽章 + tooltip
- 短句 → 分数封顶 70
- Dashboard 平均分随对话增加而更新

## 后续优化方向

### 短期（1-2周）
1. 保存音频文件（`audio_url`）供回放
2. 调整置信度阈值和评分公式
3. 添加评分详情（准确度、流利度、完整性占位）

### 中期（1-2月）
1. 实现 GOP 评分（音素级）
2. 强制对齐获取逐词/逐音素时间轴
3. 提供逐词评分反馈

### 长期
1. 接入第三方专业发音评测 API
2. 多维度评分（发音、语调、节奏）
3. 个性化评分标准

## 技术栈

- **后端**: FastAPI + SQLAlchemy + openai-whisper
- **前端**: Vue 3 + Element Plus
- **STT**: Whisper base 模型（CPU）
- **评分**: 弱评分占位（基于 STT 置信度）

## 注意事项

1. **Whisper 模型加载**: 首次调用会下载模型（~140MB），需要网络
2. **CPU 推理**: base 模型在 Intel Mac 上约 2-5 秒/句
3. **置信度计算**: 基于 `avg_logprob`，不是绝对准确
4. **评分仅供参考**: 当前是占位算法，不能作为专业评测依据

## 文件清单

### 后端
- `backend/app/services/stt_service.py` - STT 服务（增加置信度）
- `backend/app/api/voice.py` - 语音对话合并接口（新建）
- `backend/app/api/chat.py` - 历史接口返回评分
- `backend/app/main.py` - 注册 voice router

### 前端
- `frontend/src/components/MediaAudioRecorder.vue` - 录音组件简化
- `frontend/src/views/VoiceConversation.vue` - 语音对话页面（SSE 流处理 + UI）
- `frontend/src/stores/chat.js` - chatStore 历史加载保留评分

## 完成状态

✅ 所有计划功能已实现
✅ 后端接口完整
✅ 前端 UI 完整
✅ 数据库字段使用
✅ 历史加载支持
✅ Dashboard 统计支持

