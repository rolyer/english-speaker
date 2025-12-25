"""AI对话服务"""
from typing import Optional, AsyncIterator, List
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from app.core.model_config import ModelType, model_config
from app.services.local_model_service import local_model_service
import logging
import sys
import os

# 设置UTF-8编码环境
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['LC_ALL'] = 'en_US.UTF-8'
os.environ['LANG'] = 'en_US.UTF-8'

# 确保标准输出使用UTF-8编码
try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# 配置logging使用UTF-8编码
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

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
        
        elif model_type_enum == ModelType.OPENROUTER:
            # OpenRouter兼容OpenAI API格式，使用ChatOpenAI并配置base_url
            openrouter_config = self.model_config.get_openrouter_config()
            return ChatOpenAI(
                api_key=openrouter_config["api_key"],
                base_url=openrouter_config["base_url"],
                model=model_name or openrouter_config["model"],
                temperature=temperature,
                default_headers={
                    "HTTP-Referer": "https://github.com/yourusername/speaker",  # 可选：用于OpenRouter统计
                    "X-Title": "English Speaking Training for Kids"  # 可选：应用名称（必须是ASCII）
                },
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
            # 默认使用OpenRouter
            logger.warning(f"Unknown model type: {model_type}, using OpenRouter")
            openrouter_config = self.model_config.get_openrouter_config()
            return ChatOpenAI(
                api_key=openrouter_config["api_key"],
                base_url=openrouter_config["base_url"],
                model=model_name or openrouter_config["model"],
                temperature=temperature,
                default_headers={
                    "HTTP-Referer": "https://github.com/yourusername/speaker",  # 可选：用于OpenRouter统计
                    "X-Title": "English Speaking Training for Kids"  # 可选：应用名称（必须是ASCII）
                },
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
                try:
                    if hasattr(chunk, 'content'):
                        content = chunk.content
                        # 确保content是字符串类型，如果是bytes则解码
                        if isinstance(content, bytes):
                            content = content.decode('utf-8', errors='replace')
                        elif not isinstance(content, str):
                            try:
                                content = str(content)
                            except UnicodeEncodeError:
                                # 如果str()转换失败，使用repr()然后编码
                                content = repr(content).encode('utf-8', errors='replace').decode('utf-8')
                        # 确保content是有效的UTF-8字符串
                        if any(ord(c) > 127 for c in content):
                            content = content.encode('utf-8', errors='replace').decode('utf-8')
                        yield content
                    else:
                        # 确保转换为字符串时使用UTF-8编码
                        try:
                            chunk_str = str(chunk)
                            # 如果包含非ASCII字符，确保使用UTF-8编码
                            if any(ord(c) > 127 for c in chunk_str):
                                chunk_str = chunk_str.encode('utf-8', errors='replace').decode('utf-8')
                            yield chunk_str
                        except UnicodeEncodeError:
                            # 如果str()转换失败，使用repr()然后编码
                            try:
                                chunk_str = repr(chunk).encode('utf-8', errors='replace').decode('utf-8')
                                yield chunk_str
                            except:
                                yield ""
                except (UnicodeEncodeError, UnicodeDecodeError) as e:
                    # 使用 ASCII 安全的日志消息
                    logger.error("Unicode encoding error occurred")
                    # 如果遇到编码错误，尝试使用UTF-8编码
                    try:
                        if hasattr(chunk, 'content'):
                            content = chunk.content
                            if isinstance(content, bytes):
                                content = content.decode('utf-8', errors='replace')
                            else:
                                content = str(content).encode('utf-8', errors='replace').decode('utf-8')
                            yield content
                        else:
                            yield str(chunk).encode('utf-8', errors='replace').decode('utf-8')
                    except Exception as encode_error:
                        # 使用 ASCII 安全的日志消息
                        logger.error("Failed to encode chunk")
                        yield ""  # 返回空字符串而不是抛出异常


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
            # 记录错误类型
            error_type = type(e).__name__
            logger.error(f"AI chat error: {error_type}")
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
                # 确保chunk是UTF-8编码的字符串
                if isinstance(chunk, bytes):
                    chunk = chunk.decode('utf-8', errors='replace')
                elif not isinstance(chunk, str):
                    try:
                        chunk = str(chunk)
                    except UnicodeEncodeError:
                        chunk = str(chunk).encode('utf-8', errors='replace').decode('utf-8')
                yield chunk
        except Exception as e:
            # 安全地处理错误消息，避免编码问题
            error_msg = None
            try:
                error_msg = str(e)
                # 如果包含非ASCII字符，先编码再解码确保安全
                if any(ord(c) > 127 for c in error_msg):
                    error_msg = error_msg.encode('utf-8', errors='replace').decode('utf-8')
            except Exception:
                error_msg = repr(e)
            
            # 处理地区限制错误
            if error_msg and ("unsupported_country_region_territory" in error_msg or "403" in error_msg):
                # 使用 ASCII 安全的日志消息
                logger.error("AI stream chat error: region restriction")
                raise ValueError(
                    "当前地区不支持所选模型。请尝试使用其他模型，如："
                    "meta-llama/llama-3.1-8b-instruct:free, "
                    "google/gemini-pro, 或 anthropic/claude-3-haiku"
                )
            # 记录错误类型和简化的错误信息（避免编码问题）
            error_type = type(e).__name__
            logger.error(f"AI stream chat error: {error_type}")
            # 如果有安全的错误消息，也记录下来
            if error_msg:
                # 只记录前100个字符，避免过长
                safe_msg = error_msg[:100] if len(error_msg) > 100 else error_msg
                # 移除非ASCII字符
                safe_msg = ''.join(c if ord(c) < 128 else '?' for c in safe_msg)
                logger.error(f"Error details: {safe_msg}")
            raise


ai_service = AIService()

