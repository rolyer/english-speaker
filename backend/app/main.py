"""
小学生英语口语训练WEB应用 - 后端入口文件
"""
import sys
import os

# 设置UTF-8编码环境
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
if sys.stderr.encoding != 'utf-8':
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, chat, pronunciation, progress, tts, stt, voice, profile

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="面向中国小学生的英语口语对话训练WEB应用后端API",
    version=settings.APP_VERSION,
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(pronunciation.router)
app.include_router(progress.router)
app.include_router(tts.router)
app.include_router(stt.router)
app.include_router(voice.router)
app.include_router(profile.router)


@app.get("/")
async def root():
    """健康检查端点"""
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}

