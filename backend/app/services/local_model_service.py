"""本地大模型服务（Ollama）"""
from typing import Optional, AsyncIterator
from langchain_ollama import OllamaLLM, ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from app.core.model_config import model_config
import httpx


class LocalModelService:
    """本地模型服务类"""
    
    def __init__(self):
        self.base_url = model_config.ollama_base_url
        self.default_model = "llama3.2:3b"
    
    def create_llm(self, model_name: Optional[str] = None, temperature: float = 0.7) -> OllamaLLM:
        """创建Ollama LLM实例"""
        model = model_name or self.default_model
        return OllamaLLM(
            model=model,
            base_url=self.base_url,
            temperature=temperature,
        )
    
    def create_chat_model(self, model_name: Optional[str] = None, temperature: float = 0.7) -> ChatOllama:
        """创建Ollama Chat模型实例"""
        model = model_name or self.default_model
        return ChatOllama(
            model=model,
            base_url=self.base_url,
            temperature=temperature,
        )
    
    async def check_health(self) -> bool:
        """检查Ollama服务健康状态"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags", timeout=5.0)
                return response.status_code == 200
        except Exception:
            return False
    
    async def list_models(self) -> list[str]:
        """列出可用的模型"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    return [model["name"] for model in data.get("models", [])]
                return []
        except Exception:
            return []
    
    async def stream_chat(
        self,
        messages: list[BaseMessage],
        model_name: Optional[str] = None,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """流式聊天"""
        chat_model = self.create_chat_model(model_name, temperature)
        async for chunk in chat_model.astream(messages):
            if hasattr(chunk, 'content'):
                yield chunk.content
            else:
                yield str(chunk)


local_model_service = LocalModelService()

