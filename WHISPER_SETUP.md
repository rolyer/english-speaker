# Whisper 本地语音识别设置指南

本项目使用 OpenAI 的 Whisper 模型进行本地语音识别，完全免费且不需要网络请求。

## 安装步骤

### 1. 安装 FFmpeg（必需）

Whisper 需要 FFmpeg 来处理音频文件。

#### macOS:
```bash
brew install ffmpeg
```

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install ffmpeg
```

#### Windows:
1. 下载 FFmpeg: https://ffmpeg.org/download.html
2. 解压并添加到系统 PATH

### 2. 安装 Python 依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 验证安装

```bash
python -c "import whisper; print('Whisper 安装成功')"
```

## Whisper 模型说明

Whisper 提供多种模型，根据需求选择：

| 模型 | 大小 | 速度 | 准确度 | 推荐场景 |
|------|------|------|--------|----------|
| tiny | 39 MB | 最快 | 较低 | 快速测试 |
| base | 74 MB | 快 | 中等 | **推荐用于生产** |
| small | 244 MB | 中等 | 良好 | 需要更高准确度 |
| medium | 769 MB | 慢 | 很好 | 高质量需求 |
| large | 1550 MB | 最慢 | 最好 | 专业应用 |

当前配置使用 **base** 模型（速度和准确度的最佳平衡）。

### 更改模型

编辑 `backend/app/services/stt_service.py`，修改：

```python
_whisper_model = whisper.load_model("base")  # 改为 tiny, small, medium, large
```

## 首次运行

首次运行时，Whisper 会自动下载模型文件（约 74 MB）：

```bash
cd backend
uvicorn app.main:app --reload
```

模型会缓存在 `~/.cache/whisper/`，后续启动无需重新下载。

## 性能优化

### 使用 GPU 加速（可选）

如果有 NVIDIA GPU，可以启用 GPU 加速：

1. 安装 CUDA 版本的 PyTorch:
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

2. 修改 `stt_service.py`，将 `fp16=False` 改为 `fp16=True`

### CPU 优化

对于 CPU 运行：
- 使用 `tiny` 或 `base` 模型
- 保持 `fp16=False`
- 考虑使用多进程处理

## 故障排除

### 问题：ImportError: No module named 'whisper'
**解决**：运行 `pip install openai-whisper`

### 问题：RuntimeError: FFmpeg not found
**解决**：安装 FFmpeg（见上方安装步骤）

### 问题：模型加载缓慢
**原因**：首次运行需要下载模型
**解决**：等待下载完成，后续启动会很快

### 问题：识别准确度不高
**解决**：
1. 升级到更大的模型（如 `small` 或 `medium`）
2. 确保音频质量良好
3. 指定正确的语言代码

## 语言支持

Whisper 支持 99 种语言，包括：
- 英语 (en)
- 中文 (zh)
- 日语 (ja)
- 韩语 (ko)
- 西班牙语 (es)
- 法语 (fr)
- 德语 (de)
- ...等

完整列表：https://github.com/openai/whisper#available-models-and-languages

## 成本对比

| 方案 | 成本 | 速度 | 准确度 | 隐私 |
|------|------|------|--------|------|
| 本地 Whisper | 免费 | 快（无网络延迟） | 高 | 完全私密 |
| OpenAI API | $0.006/分钟 | 中等 | 高 | 数据上传到云端 |
| 浏览器 Speech API | 免费 | 快 | 中等 | 取决于浏览器 |

**推荐使用本地 Whisper**：完全免费、速度快、准确度高、保护隐私。

