# 语音识别功能设置指南

本项目使用 **本地 Whisper 模型** 进行语音识别，完全免费且保护隐私。

## 为什么使用本地 Whisper？

由于 Android Chrome 的 `SpeechRecognition` API 存在兼容性问题，我们改用更可靠的方案：

1. ✅ **完全免费** - 无需支付 API 费用
2. ✅ **速度快** - 无网络延迟
3. ✅ **准确度高** - OpenAI 的 Whisper 模型准确度极高
4. ✅ **保护隐私** - 音频数据不会上传到云端
5. ✅ **支持多语言** - 支持 99 种语言
6. ✅ **跨平台** - 在所有设备和浏览器上都能工作

## 快速安装

### 方式一：使用安装脚本（推荐）

```bash
cd /Users/qinghe/Develop/Ai/speaker
./install_whisper.sh
```

### 方式二：手动安装

#### 1. 安装 FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

#### 2. 安装 Python 依赖

```bash
cd backend
pip install -r requirements.txt
```

## 启动服务

```bash
# 启动后端
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端（新终端）
cd frontend
npm run dev
```

## 工作原理

```
用户点击录音 → MediaRecorder 录制音频 → 发送到后端 
→ Whisper 模型识别 → 返回文本 → 显示并发送给 AI
```

### 技术栈

- **前端录音**: MediaRecorder API（WebM 格式）
- **后端识别**: OpenAI Whisper 本地模型
- **模型**: base 模型（74 MB，速度和准确度平衡）

## 首次运行

首次启动后端时，Whisper 会自动下载模型：

```bash
$ uvicorn app.main:app --reload
INFO:     正在加载 Whisper 模型...
Downloading: 100%|████████████| 139M/139M [00:30<00:00, 4.63MB/s]
INFO:     Whisper 模型加载成功
INFO:     Application startup complete.
```

模型会缓存在 `~/.cache/whisper/`，后续启动无需重新下载。

## 使用方法

1. 打开语音对话页面
2. 点击录音按钮（麦克风图标）
3. 允许麦克风权限
4. 开始说话
5. 点击停止按钮
6. 等待识别（通常 1-2 秒）
7. 识别结果会自动发送给 AI

## 性能说明

### 识别速度

- **tiny 模型**: ~0.5 秒
- **base 模型**: ~1-2 秒（当前使用）
- **small 模型**: ~3-5 秒
- **medium 模型**: ~8-12 秒
- **large 模型**: ~15-25 秒

### 准确度

- **tiny**: 适合快速测试
- **base**: 日常使用足够（推荐）
- **small/medium**: 更高准确度
- **large**: 专业级准确度

## 更改模型

如果需要更高的准确度，可以升级模型：

编辑 `backend/app/services/stt_service.py`:

```python
# 将 base 改为 small, medium 或 large
_whisper_model = whisper.load_model("small")
```

重启后端服务即可。

## 故障排除

### 问题 1: FFmpeg not found

**症状**: 启动后端时报错 `RuntimeError: FFmpeg not found`

**解决**:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### 问题 2: 模型下载失败

**症状**: 下载模型时网络错误

**解决**:
1. 检查网络连接
2. 使用代理（如果在国内）
3. 手动下载模型并放到 `~/.cache/whisper/`

### 问题 3: 识别速度慢

**解决**:
1. 使用更小的模型（tiny 或 base）
2. 如果有 GPU，安装 CUDA 版本的 PyTorch
3. 确保没有其他程序占用 CPU

### 问题 4: 识别准确度不高

**解决**:
1. 升级到更大的模型（small 或 medium）
2. 确保录音环境安静
3. 说话清晰，不要太快
4. 检查麦克风质量

### 问题 5: 手机上无法录音

**症状**: 点击录音按钮没有反应

**解决**:
1. 确保使用 HTTPS 或 localhost
2. 检查浏览器麦克风权限
3. 尝试刷新页面
4. 查看浏览器控制台错误信息

## 语言支持

Whisper 支持 99 种语言，常用语言包括：

- 🇺🇸 英语 (en)
- 🇨🇳 中文 (zh)
- 🇯🇵 日语 (ja)
- 🇰🇷 韩语 (ko)
- 🇪🇸 西班牙语 (es)
- 🇫🇷 法语 (fr)
- 🇩🇪 德语 (de)
- 🇷🇺 俄语 (ru)
- 🇵🇹 葡萄牙语 (pt)
- 🇮🇹 意大利语 (it)

## 成本对比

| 方案 | 成本 | 速度 | 准确度 | 隐私 | 兼容性 |
|------|------|------|--------|------|--------|
| **本地 Whisper** | 免费 | 快 | 高 | ✅ 完全私密 | ✅ 全平台 |
| OpenAI API | $0.006/分钟 | 中等 | 高 | ⚠️ 上传云端 | ✅ 全平台 |
| 浏览器 Speech API | 免费 | 快 | 中等 | ⚠️ 取决于浏览器 | ❌ Android 有问题 |

## 更多信息

- Whisper 官方文档: https://github.com/openai/whisper
- 详细设置指南: `WHISPER_SETUP.md`
- 问题反馈: 请在项目中创建 Issue

## 总结

使用本地 Whisper 模型是最佳方案：
- ✅ 完全免费
- ✅ 速度快（1-2秒识别）
- ✅ 准确度高
- ✅ 保护隐私
- ✅ 在所有设备上都能工作

现在就开始使用吧！🎉

