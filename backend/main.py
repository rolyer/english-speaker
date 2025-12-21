"""
小学生英语口语训练WEB应用 - 后端入口文件
导入 app.main 中的 app 实例
"""
from app.main import app

# 导出 app 供 uvicorn 使用
__all__ = ["app"]

