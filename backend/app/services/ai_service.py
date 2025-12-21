"""AI对话服务"""
from typing import Optional, AsyncIterator, List
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from app.core.model_config import ModelType, model_config
from app.services.local_model_service import local_model_service
import logging

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)


class ModelRouter:
    """模型路由器"""
    
    def __init__(self):
        self.model_config = model_config
    
    def get_chat_model(
        self,
        model_type: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7
    ) -> BaseChatModel:
        """获取聊天模型实例"""
        model_type_enum = self.model_config.get_model_type(model_type)
        
        if model_type_enum == ModelType.OLLAMA:
            return local_model_service.create_chat_model(model_name, temperature)
        
        elif model_type_enum == ModelType.OPENAI:
            openai_config = self.model_config.get_openai_config()
            return ChatOpenAI(
                api_key=openai_config["api_key"],
                model=model_name or openai_config["model"],
                temperature=temperature,
            )
        
        elif model_type_enum == ModelType.QWEN:
            # 阿里百炼兼容OpenAI API格式，使用ChatOpenAI并配置base_url
            qwen_config = self.model_config.get_qwen_config()
            return ChatOpenAI(
                api_key=qwen_config["api_key"],
                base_url=qwen_config["base_url"],
                model=model_name or qwen_config["model"],
                temperature=temperature,
            )
        
        else:
            # 默认使用通义千问
            logger.warning(f"Unknown model type: {model_type}, using Qwen")
            qwen_config = self.model_config.get_qwen_config()
            return ChatOpenAI(
                api_key=qwen_config["api_key"],
                base_url=qwen_config["base_url"],
                model=model_name or qwen_config["model"],
                temperature=temperature,
            )
    
    async def chat(
        self,
        messages: List[BaseMessage],
        model_type: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """聊天（非流式）"""
        chat_model = self.get_chat_model(model_type, model_name, temperature)
        response = await chat_model.ainvoke(messages)
        return response.content if hasattr(response, 'content') else str(response)
    
    async def stream_chat(
        self,
        messages: List[BaseMessage],
        model_type: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """流式聊天"""
        chat_model = self.get_chat_model(model_type, model_name, temperature)
        
        model_type_enum = self.model_config.get_model_type(model_type)
        
        if model_type_enum == ModelType.OLLAMA:
            # 使用本地服务的流式方法
            async for chunk in local_model_service.stream_chat(messages, model_name, temperature):
                yield chunk
        else:
            # 使用LangChain的流式方法
            async for chunk in chat_model.astream(messages):
                if hasattr(chunk, 'content'):
                    yield chunk.content
                else:
                    yield str(chunk)


class AIService:
    """AI服务类"""
    
    def __init__(self):
        self.router = ModelRouter()
        from app.services.prompt_service import prompt_service
        self.prompt_service = prompt_service
    
    def create_system_message(self, scenario: Optional[str] = None) -> SystemMessage:
        """创建系统消息"""
        return self.prompt_service.create_system_message(scenario)
    
    async def chat(
        self,
        user_message: str,
        conversation_history: Optional[List[BaseMessage]] = None,
        model_type: Optional[str] = None,
        model_name: Optional[str] = None,
        scenario: Optional[str] = None
    ) -> str:
        """对话"""
        messages = [self.create_system_message(scenario)]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append(HumanMessage(content=user_message))
        
        try:
            response = await self.router.chat(messages, model_type, model_name)
            return response
        except Exception as e:
            logger.error(f"AI chat error: {e}")
            raise
    
    async def stream_chat(
        self,
        user_message: str,
        conversation_history: Optional[List[BaseMessage]] = None,
        model_type: Optional[str] = None,
        model_name: Optional[str] = None,
        scenario: Optional[str] = None
    ) -> AsyncIterator[str]:
        """流式对话"""
        messages = [self.create_system_message(scenario)]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append(HumanMessage(content=user_message))
        
        try:
            async for chunk in self.router.stream_chat(messages, model_type, model_name):
                yield chunk
        except Exception as e:
            logger.error(f"AI stream chat error: {e}")
            raise


ai_service = AIService()

