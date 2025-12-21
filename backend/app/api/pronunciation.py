"""发音评分API路由"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.services.pronunciation_service import pronunciation_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pronunciation", tags=["发音评分"])


class PronunciationRequest(BaseModel):
    """发音评分请求模型"""
    reference_text: str
    language: str = "en-US"


class PronunciationResponse(BaseModel):
    """发音评分响应模型"""
    score: float
    accuracy: Optional[float] = None
    fluency: Optional[float] = None
    completeness: Optional[float] = None
    feedback: list[str] = []
    word_scores: Optional[list] = None


@router.post("/evaluate", response_model=PronunciationResponse)
async def evaluate_pronunciation(
    reference_text: str,
    audio: UploadFile = File(...),
    language: str = "en-US",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """评估发音"""
    if not pronunciation_service.is_available():
        # 如果第三方服务不可用，返回模拟评分（用于演示）
        logger.warning("发音评分服务不可用，返回模拟评分")
        return PronunciationResponse(
            score=85.0,
            accuracy=90.0,
            fluency=80.0,
            completeness=85.0,
            feedback=pronunciation_service.generate_feedback(85.0)
        )
    
    try:
        audio_data = await audio.read()
        result = await pronunciation_service.evaluate_pronunciation(
            audio_data,
            reference_text,
            language
        )
        return PronunciationResponse(**result)
    except Exception as e:
        logger.error(f"发音评分错误: {e}")
        raise HTTPException(status_code=500, detail=f"发音评分失败: {str(e)}")


@router.get("/health")
async def health_check():
    """发音评分服务健康检查"""
    return {
        "status": "available" if pronunciation_service.is_available() else "unavailable"
    }

