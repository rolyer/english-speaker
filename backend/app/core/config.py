"""应用配置模块"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    APP_NAME: str = "小学生英语口语训练API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS配置
    CORS_ORIGINS: list[str] = ["*"]
    
    # AI模型配置
    OPENAI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None  # OpenRouter API密钥
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"  # OpenRouter Base URL
    OPENROUTER_DEFAULT_MODEL: str = "meta-llama/llama-3.1-8b-instruct:free"  # OpenRouter默认模型（全球可用）
    DASHSCOPE_API_KEY: Optional[str] = None  # 阿里百炼API密钥（保留兼容）
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # 阿里百炼Base URL（保留兼容）
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    DEFAULT_MODEL: str = "openrouter"  # openrouter, ollama, openai, qwen等
    
    # 语音服务配置
    TTS_API_KEY: Optional[str] = None
    STT_API_KEY: Optional[str] = None
    
    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

