"""TTS API路由"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.services.tts_service import tts_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tts", tags=["语音合成"])


class TTSRequest(BaseModel):
    """TTS请求模型"""
    text: str
    language: str = "en-US"
    voice: Optional[str] = None
    rate: Optional[str] = None  # 语速，如 '+0%', '-20%', '+50%'
    pitch: Optional[str] = None  # 音调，如 '+0Hz', '+5Hz', '-5Hz'


@router.post("/synthesize")
async def synthesize_speech(
    request: TTSRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """合成语音
    
    返回音频流（MP3格式）
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="文本不能为空")
    
    try:
        # 调用 TTS 服务生成音频
        audio_data = await tts_service.synthesize_speech(
            text=request.text,
            language=request.language,
            voice=request.voice,
            rate=request.rate,
            pitch=request.pitch
        )
        
        # 返回音频流
        return StreamingResponse(
            iter([audio_data]),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f'inline; filename="tts.mp3"',
                "Cache-Control": "no-cache"
            }
        )
        
    except ValueError as e:
        logger.error(f"TTS请求参数错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"TTS合成失败: {e}")
        raise HTTPException(status_code=500, detail=f"语音合成失败: {str(e)}")


@router.get("/voices")
async def list_voices(
    language: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """获取可用的语音列表
    
    Args:
        language: 可选的语言代码，用于过滤语音列表
    """
    try:
        voices = await tts_service.get_voices()
        
        if language:
            # 过滤指定语言的语音
            lang_code = language.split('-')[0] if '-' in language else language
            filtered_voices = [
                voice for voice in voices
                if voice["Locale"].startswith(language) or voice["Locale"].startswith(lang_code)
            ]
            return {"voices": filtered_voices, "count": len(filtered_voices)}
        
        return {"voices": voices, "count": len(voices)}
        
    except Exception as e:
        logger.error(f"获取语音列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取语音列表失败: {str(e)}")


@router.get("/health")
async def health_check():
    """TTS服务健康检查"""
    return {
        "status": "available" if tts_service.is_available() else "unavailable",
        "service": "edge-tts"
    }


@router.get("/cache/stats")
async def get_cache_stats(
    current_user: User = Depends(get_current_user)
):
    """获取缓存统计信息"""
    try:
        stats = tts_service.get_cache_stats()
        return stats
    except Exception as e:
        logger.error(f"获取缓存统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取缓存统计失败: {str(e)}")


@router.delete("/cache")
async def clear_cache(
    max_age_days: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    """清理缓存
    
    Args:
        max_age_days: 删除超过指定天数的缓存文件，不提供则删除所有
    """
    try:
        deleted_count = tts_service.clear_cache(max_age_days)
        return {
            "success": True,
            "deleted_count": deleted_count,
            "message": f"成功清理 {deleted_count} 个缓存文件"
        }
    except Exception as e:
        logger.error(f"清理缓存失败: {e}")
        raise HTTPException(status_code=500, detail=f"清理缓存失败: {str(e)}")

