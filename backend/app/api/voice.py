"""语音对话API路由 - 合并STT、评分和流式对话"""
import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.conversation import Conversation, Message
from app.models.user import User
from app.services.ai_service import ai_service
from app.services.stt_service import stt_service
from app.api.chat import get_conversation_history  # 复用现有历史构建

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/voice", tags=["语音对话"])


def weak_pronunciation_score(text: str, conf: Optional[float], low_conf: bool) -> int:
    """
    弱评分占位算法：基于STT置信度的简单评分
    
    Args:
        text: 识别文本
        conf: STT置信度 (0..1)
        low_conf: 是否低置信度
    
    Returns:
        0-100的评分
    """
    # 基础分数：60-100，和置信度强相关
    c = 0.5 if conf is None else max(0.0, min(1.0, float(conf)))
    score = int(round(60 + 40 * c))
    
    # 低置信度时封顶，避免"看起来很假"
    if low_conf:
        score = min(score, 75)
    
    # 短句（<2词）通常不稳定，降分
    if len((text or "").split()) < 2:
        score = min(score, 70)
    
    return max(0, min(100, score))


@router.post("/chat/stream")
async def voice_chat_stream(
    audio: UploadFile = File(...),
    language: str = Form("en"),
    conversation_id: Optional[int] = Form(None),
    scenario: Optional[str] = Form(None),
    model_type: Optional[str] = Form(None),
    model_name: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    语音对话流式接口：上传音频 -> STT -> 评分 -> 保存用户消息 -> 流式AI回复
    
    返回SSE流，包含：
    - meta: 用户消息元数据（含评分、置信度）
    - chunk: AI回复的文本片段
    - done: 完成标记
    - error: 错误信息
    """
    try:
        # 1) 获取或创建对话会话
        if conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id,
            ).first()
            if not conversation:
                raise HTTPException(status_code=404, detail="对话会话不存在")
            if scenario and conversation.scenario != scenario:
                conversation.scenario = scenario
                db.commit()
        else:
            conversation = Conversation(
                user_id=current_user.id,
                scenario=scenario or "general"
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        # 2) 读取音频数据
        audio_data = await audio.read()
        if not audio_data:
            raise HTTPException(status_code=400, detail="音频文件为空")

        # 3) STT转写（带置信度）
        logger.info(f"开始语音识别，音频大小: {len(audio_data)} bytes")
        stt_result = await stt_service.transcribe_with_confidence(audio_data, language)
        text = stt_result["text"]
        conf = stt_result.get("confidence")
        low_conf = bool(stt_result.get("low_confidence"))
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="未识别到有效语音内容")

        # 4) 计算弱评分
        score = weak_pronunciation_score(text, conf, low_conf)
        conf_str = f"{conf:.2f}" if conf is not None else "N/A"
        logger.info(f"识别文本: {text}, 置信度: {conf_str}, 评分: {score}")

        # 5) 保存用户消息（含评分）
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=text,
            pronunciation_score=float(score),
        )
        db.add(user_message)
        db.commit()
        db.refresh(user_message)

        # 6) 获取对话历史（包含刚保存的用户消息）
        history = get_conversation_history(db, conversation.id)

        # 7) 流式生成AI回复
        async def generate():
            # 先发送meta，让前端立刻插入用户消息（含评分/低置信度）
            yield "data: " + json.dumps(
                {
                    "type": "meta",
                    "conversation_id": conversation.id,
                    "user_message": {
                        "id": user_message.id,
                        "role": "user",
                        "content": text,
                        "created_at": user_message.created_at.isoformat() if user_message.created_at else None,
                        "pronunciation_score": score,
                        "stt_confidence": conf,
                        "stt_low_confidence": low_conf,
                    },
                    "done": False,
                },
                ensure_ascii=False,
            ) + "\n\n"

            full_response = ""
            try:
                async for chunk in ai_service.stream_chat(
                    text,
                    history,
                    model_type,
                    model_name,
                    scenario or conversation.scenario,
                ):
                    # 确保chunk是字符串
                    if isinstance(chunk, bytes):
                        chunk = chunk.decode("utf-8", errors="replace")
                    chunk = str(chunk)
                    full_response += chunk
                    
                    yield "data: " + json.dumps(
                        {"type": "chunk", "chunk": chunk, "done": False},
                        ensure_ascii=False,
                    ) + "\n\n"

                # 保存AI回复
                ai_message = Message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=full_response,
                )
                db.add(ai_message)
                db.commit()
                db.refresh(ai_message)

                yield "data: " + json.dumps(
                    {
                        "type": "done",
                        "done": True,
                        "conversation_id": conversation.id,
                        "assistant_message_id": ai_message.id,
                    },
                    ensure_ascii=False,
                ) + "\n\n"
                
            except Exception as e:
                logger.error(f"AI流式回复错误: {str(e)}")
                yield "data: " + json.dumps(
                    {"type": "error", "error": str(e)},
                    ensure_ascii=False,
                ) + "\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"语音对话失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"语音对话失败: {str(e)}")

