"""对话API路由"""
import sys
import os
import json
import logging

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

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.services.ai_service import ai_service
from app.services.local_model_service import local_model_service
from langchain_core.messages import HumanMessage, AIMessage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["对话"])


class ChatRequest(BaseModel):
    """对话请求模型"""
    message: str
    conversation_id: Optional[int] = None
    model_type: Optional[str] = None
    model_name: Optional[str] = None
    scenario: Optional[str] = None


class ChatResponse(BaseModel):
    """对话响应模型"""
    response: str
    conversation_id: int
    message_id: int


class ConversationResponse(BaseModel):
    """对话会话响应模型"""
    id: int
    scenario: str
    started_at: str
    messages: List[dict]
    
    class Config:
        from_attributes = True


def get_conversation_history(db: Session, conversation_id: int) -> List:
    """获取对话历史"""
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()
    
    history = []
    for msg in messages:
        if msg.role == "user":
            history.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            history.append(AIMessage(content=msg.content))
    
    return history


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """对话接口"""
    # 获取或创建对话会话
    if request.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="对话会话不存在")
    else:
        conversation = Conversation(user_id=current_user.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # 获取对话历史
    history = get_conversation_history(db, conversation.id)
    
    # 调用AI服务
    try:
        response_text = await ai_service.chat(
            request.message,
            history,
            request.model_type,
            request.model_name,
            request.scenario or conversation.scenario
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI服务错误: {str(e)}")
    
    # 保存用户消息
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    
    # 保存AI回复
    ai_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response_text
    )
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)
    
    return ChatResponse(
        response=response_text,
        conversation_id=conversation.id,
        message_id=ai_message.id
    )


@router.post("/stream")
async def stream_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """流式对话接口"""
    # 获取或创建对话会话
    if request.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="对话会话不存在")
    else:
        conversation = Conversation(user_id=current_user.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # 获取对话历史
    history = get_conversation_history(db, conversation.id)
    
    # 保存用户消息
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    db.commit()
    
    async def generate():
        full_response = ""
        try:
            async for chunk in ai_service.stream_chat(
                request.message,
                history,
                request.model_type,
                request.model_name,
                request.scenario or conversation.scenario
            ):
                # 确保chunk是字符串类型，正确处理编码
                try:
                    if isinstance(chunk, bytes):
                        chunk = chunk.decode('utf-8', errors='replace')
                    elif not isinstance(chunk, str):
                        try:
                            chunk = str(chunk)
                        except UnicodeEncodeError:
                            chunk = repr(chunk).encode('utf-8', errors='replace').decode('utf-8')
                    
                    # 确保chunk是有效的UTF-8字符串
                    if any(ord(c) > 127 for c in chunk):
                        chunk = chunk.encode('utf-8', errors='replace').decode('utf-8')
                    
                    full_response += chunk
                    # 使用ensure_ascii=False以正确处理非ASCII字符（如中文）
                    yield f"data: {json.dumps({'chunk': chunk, 'done': False}, ensure_ascii=False)}\n\n"
                except (UnicodeEncodeError, UnicodeDecodeError) as encode_error:
                    # 如果编码失败，跳过这个chunk或使用空字符串
                    # 使用 ASCII 安全的日志消息
                    logger.error("Encoding error in chunk")
                    continue
            
            # 保存AI回复
            ai_message = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=full_response
            )
            db.add(ai_message)
            db.commit()
            
            yield f"data: {json.dumps({'chunk': '', 'done': True, 'conversation_id': conversation.id}, ensure_ascii=False)}\n\n"
        except Exception as e:
            # 安全地处理错误消息，避免编码问题
            error_msg = None
            try:
                error_msg = str(e)
                # 如果包含非ASCII字符，先编码再解码确保安全
                if isinstance(error_msg, bytes):
                    error_msg = error_msg.decode('utf-8', errors='replace')
                elif any(ord(c) > 127 for c in error_msg):
                    error_msg = error_msg.encode('utf-8', errors='replace').decode('utf-8')
            except Exception:
                error_msg = "处理请求时发生错误"
            
            # 记录错误类型和简化的错误信息
            error_type = type(e).__name__
            logger.error(f"Stream chat error: {error_type}")
            # 记录安全的错误详情
            if error_msg:
                safe_msg = error_msg[:100] if len(error_msg) > 100 else error_msg
                safe_msg = ''.join(c if ord(c) < 128 else '?' for c in safe_msg)
                logger.error(f"Error details: {safe_msg}")
            
            # 确保错误消息也能正确处理非ASCII字符
            try:
                yield f"data: {json.dumps({'error': error_msg}, ensure_ascii=False)}\n\n"
            except Exception:
                # 如果JSON序列化失败，使用安全的错误消息
                yield "data: {\"error\": \"处理请求时发生错误\"}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的对话会话列表"""
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.started_at.desc()).limit(20).all()
    
    result = []
    for conv in conversations:
        messages = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).order_by(Message.created_at).all()
        
        result.append(ConversationResponse(
            id=conv.id,
            scenario=conv.scenario,
            started_at=conv.started_at.isoformat(),
            messages=[
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        ))
    
    return result


@router.get("/health")
async def health_check():
    """AI服务健康检查"""
    is_healthy = await local_model_service.check_health()
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "ollama_available": is_healthy
    }

