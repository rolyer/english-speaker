# 部署文档

本文档说明如何部署应用到生产环境。

## 前置要求

- Docker Engine 20.10+
- Docker Compose 2.0+
- 至少4GB可用内存（如果使用本地模型，建议8GB+）
- 域名和SSL证书（可选，用于HTTPS）

## 环境准备

### 1. 克隆代码

```bash
git clone <repository-url>
cd speaker
```

### 2. 配置环境变量

创建 `.env.prod` 文件：

```env
# 数据库配置
DB_USER=speaker
DB_PASSWORD=<strong-password>
DB_NAME=speaker
DATABASE_URL=postgresql://speaker:<strong-password>@db:5432/speaker

# JWT配置
SECRET_KEY=<generate-strong-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API配置
API_BASE_URL=https://your-domain.com
DEFAULT_MODEL=ollama

# AI服务API密钥（可选）
OPENAI_API_KEY=<your-openai-key>
TTS_API_KEY=<your-tts-key>
STT_API_KEY=<your-stt-key>

# Ollama配置
OLLAMA_BASE_URL=http://ollama:11434
```

### 3. 生成密钥

```bash
# 生成SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Docker部署

### 1. 构建镜像

```bash
docker-compose -f docker-compose.prod.yml build
```

### 2. 启动服务

```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

### 3. 初始化数据库

```bash
# 数据库表会自动创建，如果需要迁移可以使用Alembic
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### 4. 下载Ollama模型（如果使用本地模型）

```bash
docker-compose -f docker-compose.prod.yml exec ollama ollama pull llama3.2:3b
```

## Nginx配置（可选）

如果需要使用Nginx作为反向代理，创建 `nginx/nginx.conf`：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## SSL配置（HTTPS）

### 使用Let's Encrypt

```bash
# 安装certbot
sudo apt-get install certbot

# 获取证书
sudo certbot certonly --standalone -d your-domain.com

# 配置Nginx使用SSL证书
```

## 监控和日志

### 查看日志

```bash
# 所有服务日志
docker-compose -f docker-compose.prod.yml logs -f

# 特定服务日志
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f ollama
```

### 健康检查

```bash
# 后端健康检查
curl http://localhost:8000/health

# 前端健康检查
curl http://localhost/health

# Ollama健康检查
curl http://localhost:11434/api/tags
```

## 备份和恢复

### 备份数据库

```bash
docker-compose -f docker-compose.prod.yml exec db pg_dump -U speaker speaker > backup_$(date +%Y%m%d).sql
```

### 恢复数据库

```bash
docker-compose -f docker-compose.prod.yml exec -T db psql -U speaker speaker < backup_20240101.sql
```

### 备份Ollama模型

```bash
docker run --rm -v speaker_ollama-data:/data -v $(pwd):/backup alpine tar czf /backup/ollama_backup_$(date +%Y%m%d).tar.gz /data
```

## 性能优化

### 1. 启用Gzip压缩

已在Nginx配置中启用。

### 2. 使用CDN

将静态资源部署到CDN。

### 3. 数据库优化

- 定期清理旧数据
- 添加适当的索引
- 配置连接池

### 4. 缓存策略

- 使用Redis缓存频繁访问的数据
- 配置HTTP缓存头

## 安全建议

1. **修改默认密码**：生产环境必须修改所有默认密码
2. **使用HTTPS**：配置SSL证书启用HTTPS
3. **限制访问**：使用防火墙限制数据库和Ollama的外部访问
4. **定期更新**：保持Docker镜像和依赖的更新
5. **监控日志**：定期检查日志文件，发现异常
6. **备份数据**：定期备份数据库和重要文件

## 故障排查

### 服务无法启动

1. 检查端口是否被占用
2. 查看容器日志
3. 检查环境变量配置

### 数据库连接失败

1. 检查数据库容器状态
2. 验证连接字符串
3. 检查网络配置

### Ollama模型无法加载

1. 检查Ollama服务状态
2. 验证模型是否已下载
3. 检查资源限制

## 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建镜像
docker-compose -f docker-compose.prod.yml build

# 重启服务
docker-compose -f docker-compose.prod.yml up -d --force-recreate
```

## 下一步

- 查看 [Docker使用指南](docker.md) 了解详细配置
- 查看 [本地大模型配置](local_models.md) 了解Ollama使用

