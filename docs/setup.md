# 开发环境配置文档

本文档说明如何配置开发环境。

## 前置要求

- Python 3.9+
- Node.js 18+
- Docker & Docker Compose（可选）
- uv（Python包管理工具）
- nvm（Node.js版本管理工具）

## 安装开发工具

### 1. 安装 uv (Python包管理)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或使用pip
pip install uv

# 验证安装
uv --version
```

### 2. 安装 nvm (Node.js版本管理)

```bash
# macOS/Linux
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 重新加载shell配置
source ~/.bashrc  # 或 source ~/.zshrc

# 验证安装
nvm --version
```

## 后端环境设置

### 1. 进入后端目录

```bash
cd backend
```

### 2. 使用uv初始化项目（如果还未初始化）

```bash
uv init
```

### 3. 安装依赖

```bash
uv sync
```

### 4. 激活虚拟环境

```bash
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 5. 运行开发服务器

```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 前端环境设置

### 1. 进入前端目录

```bash
cd frontend
```

### 2. 使用nvm安装指定Node.js版本

```bash
nvm install
nvm use
```

### 3. 安装npm依赖

```bash
npm install
```

### 4. 运行开发服务器

```bash
npm run dev
```

## 环境变量配置

### 后端环境变量

创建 `backend/.env` 文件：

```env
# 数据库配置
DATABASE_URL=sqlite:///./app.db
# 或 PostgreSQL
# DATABASE_URL=postgresql://user:password@localhost:5432/speaker

# JWT密钥
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI模型配置
OPENAI_API_KEY=your-openai-api-key
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=ollama  # 或 openai, qwen, wenxin等

# 语音服务配置
TTS_API_KEY=your-tts-api-key
STT_API_KEY=your-stt-api-key
```

### 前端环境变量

创建 `frontend/.env` 文件：

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=小学生英语口语训练
```

## 代码规范

### Python代码规范

项目使用以下工具进行代码格式化：

- **black**: 代码格式化
- **ruff**: 代码检查和格式化
- **mypy**: 类型检查

```bash
# 格式化代码
black .
ruff check --fix .

# 类型检查
mypy .
```

### JavaScript/TypeScript代码规范

项目使用ESLint和Prettier：

```bash
# 检查代码
npm run lint

# 格式化代码
npm run format
```

## 常见问题

### uv命令未找到

确保uv已正确安装并添加到PATH环境变量中。

### nvm命令未找到

确保nvm已正确安装，并重新加载shell配置：
```bash
source ~/.bashrc  # 或 source ~/.zshrc
```

### 端口被占用

如果8000端口被占用，可以修改端口：
```bash
uvicorn main:app --reload --port 8001
```

## 下一步

- 查看 [Docker使用指南](docker.md) 了解Docker部署
- 查看 [本地大模型配置](local_models.md) 了解本地模型设置

