"""对话API路由"""
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
import json

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
                full_response += chunk
                yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
            
            # 保存AI回复
            ai_message = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=full_response
            )
            db.add(ai_message)
            db.commit()
            
            yield f"data: {json.dumps({'chunk': '', 'done': True, 'conversation_id': conversation.id})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
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

