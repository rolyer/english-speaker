# Docker使用文档

本文档说明如何使用Docker部署和运行应用。

## 前置要求

- Docker Engine 20.10+
- Docker Compose 2.0+

## 快速开始

### 开发环境

```bash
# 启动所有服务（包括Ollama）
docker-compose up -d

# 启动服务（不包含Ollama）
docker-compose up -d --scale ollama=0

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f ollama

# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

### 生产环境

```bash
# 创建环境变量文件
cp .env.example .env.prod
# 编辑 .env.prod 文件，设置必要的环境变量

# 启动生产环境
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 停止服务
docker-compose -f docker-compose.prod.yml down
```

## 服务说明

### Backend服务

- **端口**: 8000
- **健康检查**: http://localhost:8000/health
- **API文档**: http://localhost:8000/docs

### Frontend服务

- **端口**: 3000 (开发环境) / 80 (生产环境)
- **访问**: http://localhost:3000

### 数据库服务

- **类型**: PostgreSQL 15
- **端口**: 5432
- **默认用户**: speaker
- **默认密码**: speaker123 (开发环境，生产环境需修改)
- **数据库名**: speaker

### Ollama服务（本地大模型）

- **端口**: 11434
- **API**: http://localhost:11434
- **模型存储**: 持久化在 `ollama-data` 卷中

#### 下载模型

```bash
# 进入Ollama容器
docker-compose exec ollama bash

# 下载模型
ollama pull llama3.2:3b
ollama pull qwen2.5:7b

# 或直接执行
docker-compose exec ollama ollama pull llama3.2:3b
```

#### 查看已安装的模型

```bash
docker-compose exec ollama ollama list
```

## 环境变量配置

### 开发环境

编辑 `docker-compose.yml` 中的环境变量部分，或创建 `.env` 文件。

### 生产环境

创建 `.env.prod` 文件：

```env
# 数据库配置
DB_USER=speaker
DB_PASSWORD=your-secure-password
DB_NAME=speaker
DATABASE_URL=postgresql://speaker:your-secure-password@db:5432/speaker

# JWT配置
SECRET_KEY=your-secret-key-here

# API配置
API_BASE_URL=https://your-domain.com
DEFAULT_MODEL=ollama

# AI服务API密钥
OPENAI_API_KEY=your-openai-key
TTS_API_KEY=your-tts-key
STT_API_KEY=your-stt-key
```

## 数据持久化

以下数据卷用于持久化数据：

- `db-data`: PostgreSQL数据库数据
- `backend-data`: 后端应用数据
- `uploads-data`: 用户上传的文件
- `ollama-data`: Ollama模型文件

## GPU支持（可选）

如果需要GPU加速Ollama，需要：

1. 安装NVIDIA Docker运行时
2. 在 `docker-compose.yml` 中取消GPU相关注释
3. 确保Docker可以访问GPU

```bash
# 测试GPU访问
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

## 常用命令

### 构建镜像

```bash
# 构建所有服务
docker-compose build

# 构建特定服务
docker-compose build backend

# 重新构建（不使用缓存）
docker-compose build --no-cache
```

### 进入容器

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入数据库容器
docker-compose exec db psql -U speaker -d speaker

# 进入Ollama容器
docker-compose exec ollama bash
```

### 查看资源使用

```bash
# 查看容器资源使用
docker stats

# 查看特定容器
docker stats speaker-backend
```

### 备份和恢复

```bash
# 备份数据库
docker-compose exec db pg_dump -U speaker speaker > backup.sql

# 恢复数据库
docker-compose exec -T db psql -U speaker speaker < backup.sql

# 备份Ollama模型
docker run --rm -v speaker_ollama-data:/data -v $(pwd):/backup alpine tar czf /backup/ollama-backup.tar.gz /data
```

## 故障排查

### 服务无法启动

1. 检查端口是否被占用：
```bash
lsof -i :8000
lsof -i :3000
lsof -i :5432
```

2. 查看服务日志：
```bash
docker-compose logs [service_name]
```

3. 检查容器状态：
```bash
docker-compose ps
```

### 数据库连接失败

1. 确保数据库服务已启动：
```bash
docker-compose ps db
```

2. 检查数据库健康状态：
```bash
docker-compose exec db pg_isready -U speaker
```

3. 查看数据库日志：
```bash
docker-compose logs db
```

### Ollama模型无法加载

1. 检查Ollama服务状态：
```bash
docker-compose exec ollama curl http://localhost:11434/api/tags
```

2. 查看Ollama日志：
```bash
docker-compose logs ollama
```

3. 检查模型是否已下载：
```bash
docker-compose exec ollama ollama list
```

## 性能优化

### 开发环境

- 使用卷挂载实现代码热重载
- 减少不必要的服务（如不使用Ollama可关闭）

### 生产环境

- 使用多阶段构建减小镜像大小
- 启用GPU加速（如果可用）
- 配置适当的资源限制
- 使用CDN加速静态资源

## 安全建议

1. **修改默认密码**: 生产环境必须修改数据库密码
2. **使用环境变量**: 敏感信息通过环境变量传递，不要硬编码
3. **限制网络访问**: 生产环境限制数据库和Ollama的外部访问
4. **定期更新镜像**: 保持Docker镜像和依赖的更新
5. **使用非root用户**: 容器内使用非root用户运行应用

## 下一步

- 查看 [开发环境配置](setup.md) 了解本地开发设置
- 查看 [本地大模型配置](local_models.md) 了解Ollama使用

