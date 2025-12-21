# 小学生英语口语训练WEB应用

一个面向中国小学生的英语口语对话训练WEB应用，通过AI大模型提供趣味化、生活化的对话练习，自动引导和鼓励学生开口，并提供发音纠正功能。

## 技术栈

- **后端**: Python 3.9+, FastAPI, LangChain, SQLAlchemy, PostgreSQL/SQLite
- **前端**: Vue 3, TypeScript, Element Plus / Ant Design Vue
- **AI模型**: 支持云端模型（OpenAI、通义千问、文心一言、智谱AI）和本地大模型（Ollama、LocalAI等）
- **语音服务**: Web Speech API + 第三方TTS API + 发音评分API
- **容器化**: Docker, Docker Compose

## 项目结构

```
speaker/
├── backend/          # Python后端
├── frontend/         # Vue3前端
├── docs/            # 文档
└── docker-compose.yml
```

## 快速开始

### 前置要求

- Python 3.9+
- Node.js 18+
- Docker & Docker Compose（可选）
- uv（Python包管理工具）
- nvm（Node.js版本管理工具）

### 安装开发工具

#### 安装 uv
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 安装 nvm
```bash
# macOS/Linux
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
```

### 开发环境设置

#### 后端设置
```bash
cd backend
uv sync
source .venv/bin/activate  # Linux/macOS
```

#### 前端设置
```bash
cd frontend
nvm install
nvm use
npm install
```

### Docker部署（推荐）

```bash
# 开发环境
docker-compose up -d

# 生产环境
docker-compose -f docker-compose.prod.yml up -d
```

## 开发文档

详细文档请查看 [docs/](docs/) 目录：
- [开发环境配置](docs/setup.md)
- [Docker使用指南](docs/docker.md)
- [本地大模型配置](docs/local_models.md)

## 许可证

MIT License

