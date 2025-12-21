"""
小学生英语口语训练WEB应用 - 后端入口文件
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="小学生英语口语训练API",
    description="面向中国小学生的英语口语对话训练WEB应用后端API",
    version="0.1.0",
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境，生产环境需要配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """健康检查端点"""
    return {"message": "小学生英语口语训练API", "status": "running"}


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}

