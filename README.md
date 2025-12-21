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

## 启动应用

### 方式一：Docker启动（推荐，最简单）

一键启动所有服务（包括数据库和Ollama）：

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

访问地址：
- 前端：http://localhost:3000
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

### 方式二：本地开发启动

分别启动前后端服务：

**启动后端**：
```bash
cd backend
uv sync
source .venv/bin/activate  # Linux/macOS
# 创建 .env 文件
cat > .env << EOF
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=dev-secret-key-change-in-production
OLLAMA_BASE_URL=http://localhost:11434
DASHSCOPE_API_KEY=sk-02ab4cf141084b21a6d0a172e57332b2
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
DEFAULT_MODEL=qwen
EOF
# 启动服务
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**启动前端**（新终端）：
```bash
cd frontend
nvm install && nvm use
npm install
# 创建 .env 文件
cat > .env << EOF
VITE_API_BASE_URL=http://localhost:8000
EOF
# 启动服务
npm run dev
```

详细启动说明请查看 [开发环境配置文档](docs/setup.md)

## 开发文档

详细文档请查看 [docs/](docs/) 目录：
- [开发环境配置](docs/setup.md)
- [Docker使用指南](docs/docker.md)
- [本地大模型配置](docs/local_models.md)

## 许可证

MIT License

