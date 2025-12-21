# Speaker Backend

小学生英语口语训练WEB应用后端服务

## 技术栈

- Python 3.9+
- FastAPI
- LangChain
- SQLAlchemy
- PostgreSQL/SQLite

## 安装依赖

```bash
uv sync
```

## 运行开发服务器

```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 环境变量

创建 `.env` 文件：

```env
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=dev-secret-key-change-in-production
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=ollama
```

更多信息请查看项目根目录的 [README.md](../README.md) 和 [docs/setup.md](../docs/setup.md)。

