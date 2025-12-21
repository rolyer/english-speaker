# 本地大模型配置文档

本文档说明如何配置和使用本地大模型（Ollama）。

## Ollama简介

Ollama是一个本地运行大语言模型的工具，支持多种开源模型，无需API密钥，数据完全本地处理。

## 安装Ollama

### 使用Docker（推荐）

```bash
# 拉取Ollama镜像
docker pull ollama/ollama

# 运行Ollama容器
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

### 本地安装

访问 [Ollama官网](https://ollama.ai) 下载对应平台的安装包。

## 下载模型

### 推荐模型

```bash
# 轻量级模型（适合资源受限环境）
ollama pull llama3.2:3b

# 中文友好模型
ollama pull qwen2.5:7b

# 性能平衡模型
ollama pull mistral:7b

# 高质量对话模型
ollama pull llama3.1:8b
```

### 在Docker容器中下载

```bash
# 进入容器
docker exec -it ollama bash

# 下载模型
ollama pull llama3.2:3b
```

## 配置应用

### 环境变量

在 `backend/.env` 文件中配置：

```env
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=ollama
```

### Docker Compose配置

在 `docker-compose.yml` 中已经包含了Ollama服务配置，直接启动即可：

```bash
docker-compose up -d ollama
```

## 使用本地模型

应用会自动检测Ollama服务是否可用，如果可用则使用本地模型，否则可以配置使用云端模型作为备选。

### 模型切换

在对话API请求中可以指定模型类型：

```json
{
  "message": "Hello",
  "model_type": "ollama",
  "model_name": "llama3.2:3b"
}
```

## 性能优化

### GPU加速（可选）

如果系统有NVIDIA GPU，可以启用GPU加速：

1. 安装NVIDIA Docker运行时
2. 在 `docker-compose.yml` 中取消GPU相关注释
3. 重启容器

### 资源限制

在 `docker-compose.yml` 中可以设置资源限制：

```yaml
ollama:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 4G
```

## 常见问题

### Ollama服务无法连接

1. 检查Ollama容器是否运行：`docker ps | grep ollama`
2. 检查端口是否正确：`curl http://localhost:11434/api/tags`
3. 检查网络配置：确保后端可以访问Ollama服务

### 模型下载失败

1. 检查网络连接
2. 尝试手动下载：`ollama pull <model_name>`
3. 检查磁盘空间是否充足

### 响应速度慢

1. 使用更小的模型（如3B模型）
2. 启用GPU加速
3. 增加系统内存

## 模型管理

### 查看已安装的模型

```bash
ollama list
```

### 删除模型

```bash
ollama rm <model_name>
```

### 查看模型信息

```bash
ollama show <model_name>
```

## 下一步

- 查看 [Docker使用指南](docker.md) 了解完整部署
- 查看 [开发环境配置](setup.md) 了解本地开发

