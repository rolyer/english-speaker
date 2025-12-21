"""模型配置管理"""
from enum import Enum
from typing import Optional
from app.core.config import settings


class ModelType(str, Enum):
    """模型类型枚举"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    QWEN = "qwen"
    WENXIN = "wenxin"
    ZHIPU = "zhipu"


class ModelConfig:
    """模型配置类"""
    
    def __init__(self):
        self.default_model = settings.DEFAULT_MODEL
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.openai_api_key = settings.OPENAI_API_KEY
        self.dashscope_api_key = settings.DASHSCOPE_API_KEY
        self.dashscope_base_url = settings.DASHSCOPE_BASE_URL
    
    def get_model_type(self, model_name: Optional[str] = None) -> ModelType:
        """获取模型类型"""
        model = model_name or self.default_model
        try:
            return ModelType(model.lower())
        except ValueError:
            return ModelType.QWEN  # 默认使用通义千问
    
    def get_ollama_config(self) -> dict:
        """获取Ollama配置"""
        return {
            "base_url": self.ollama_base_url,
            "model": "llama3.2:3b",  # 默认模型
            "temperature": 0.7,
        }
    
    def get_openai_config(self) -> dict:
        """获取OpenAI配置"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        return {
            "api_key": self.openai_api_key,
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
        }
    
    def get_qwen_config(self) -> dict:
        """获取通义千问配置"""
        if not self.dashscope_api_key:
            raise ValueError("DashScope API key not configured")
        return {
            "api_key": self.dashscope_api_key,
            "base_url": self.dashscope_base_url,
            "model": "qwen-turbo",  # 或 qwen-plus, qwen-max
            "temperature": 0.7,
        }


model_config = ModelConfig()

