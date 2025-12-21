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

### 5. 创建环境变量文件

创建 `backend/.env` 文件：

```bash
cat > .env << EOF
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=ollama
EOF
```

### 6. 运行开发服务器

```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将在 http://localhost:8000 启动，API文档在 http://localhost:8000/docs

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

### 4. 创建环境变量文件

创建 `frontend/.env` 文件：

```bash
cat > .env << EOF
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=小学生英语口语训练
EOF
```

### 5. 运行开发服务器

```bash
npm run dev
```

前端服务将在 http://localhost:3000 启动（Vite默认端口）

## 启动应用

有两种方式启动应用：**Docker方式**（推荐，最简单）和**本地开发方式**（适合调试）。

### 方式一：Docker启动（推荐）

最简单的方式，一键启动所有服务（包括数据库和Ollama）：

```bash
# 1. 进入项目根目录
cd /Users/qinghe/Develop/Ai/speaker

# 2. 启动所有服务
docker-compose up -d

# 3. 查看服务状态
docker-compose ps

# 4. 查看日志
docker-compose logs -f

# 5. 如果需要下载Ollama模型（可选）
docker-compose exec ollama ollama pull llama3.2:3b
```

访问地址：
- **前端**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **Ollama**: http://localhost:11434

停止服务：
```bash
docker-compose down
```

### 方式二：本地开发启动

适合需要调试或修改代码的场景，需要分别启动前后端：

#### 启动后端（终端1）

```bash
# 进入后端目录
cd backend

# 安装依赖（首次运行）
uv sync

# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# Windows: .venv\Scripts\activate

# 创建.env文件（如果还没有）
cat > .env << EOF
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=dev-secret-key-change-in-production
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=ollama
EOF

# 启动后端服务
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 启动前端（终端2）

```bash
# 进入前端目录
cd frontend

# 安装依赖（首次运行）
nvm install
nvm use
npm install

# 创建.env文件（如果还没有）
cat > .env << EOF
VITE_API_BASE_URL=http://localhost:8000
EOF

# 启动前端开发服务器
npm run dev
```

访问地址：
- **前端**: http://localhost:3000（Vite默认端口）
- **后端API**: http://localhost:8000

#### 启动数据库（可选，如果使用PostgreSQL）

如果使用PostgreSQL而不是SQLite，需要单独启动数据库：

```bash
# 使用Docker启动PostgreSQL
docker run -d \
  --name speaker-db \
  -e POSTGRES_USER=speaker \
  -e POSTGRES_PASSWORD=speaker123 \
  -e POSTGRES_DB=speaker \
  -p 5432:5432 \
  postgres:15-alpine
```

#### 启动Ollama（可选，如果使用本地模型）

```bash
# 使用Docker启动Ollama
docker run -d \
  --name ollama \
  -v ollama-data:/root/.ollama \
  -p 11434:11434 \
  ollama/ollama

# 下载模型
docker exec ollama ollama pull llama3.2:3b
```

### 快速检查清单

启动前确认：

1. ✅ 后端依赖已安装：`cd backend && uv sync`
2. ✅ 前端依赖已安装：`cd frontend && npm install`
3. ✅ 环境变量已配置：创建 `backend/.env` 和 `frontend/.env`
4. ✅ 端口未被占用：8000（后端）、3000（前端）

### 推荐开发流程

- **首次启动**：使用 Docker Compose（最简单，一键启动所有服务）
- **日常开发**：本地启动前后端（热重载更快，便于调试）
- **测试完整环境**：使用 Docker Compose（确保环境一致性）

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

**后端修改端口**：
```bash
uvicorn main:app --reload --port 8001
```

**前端修改端口**：
```bash
npm run dev -- --port 3001
```

**检查端口占用**：
```bash
# macOS/Linux
lsof -i :8000
lsof -i :3000

# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :3000
```

### 数据库连接失败

- 如果使用SQLite，确保 `backend/app.db` 文件可写
- 如果使用PostgreSQL，确保数据库服务已启动
- 检查环境变量 `DATABASE_URL` 配置是否正确

### Ollama连接失败

- 确保Ollama服务已启动：`curl http://localhost:11434/api/tags`
- 如果使用Docker，检查容器状态：`docker ps | grep ollama`
- 检查环境变量 `OLLAMA_BASE_URL` 配置是否正确

## 下一步

- 查看 [Docker使用指南](docker.md) 了解Docker部署
- 查看 [本地大模型配置](local_models.md) 了解本地模型设置

