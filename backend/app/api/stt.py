"""语音识别API"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.stt_service import stt_service
from app.api.auth import get_current_user
from app.models.user import User
import logging

router = APIRouter(prefix="/api/stt", tags=["语音识别"])
logger = logging.getLogger(__name__)


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = "en",
    current_user: User = Depends(get_current_user)
):
    """
    语音转文字接口
    
    Args:
        file: 音频文件（WebM/OGG/MP3/WAV）
        language: 语言代码（en/zh）
        current_user: 当前用户
    
    Returns:
        转录的文本
    """
    try:
        # 读取音频数据
        audio_data = await file.read()
        
        if not audio_data:
            raise HTTPException(status_code=400, detail="音频文件为空")
        
        # 调用语音识别服务
        text = await stt_service.transcribe_audio(audio_data, language)
        
        return {
            "text": text,
            "language": language
        }
        
    except ValueError as e:
        logger.error(f"参数错误: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"语音识别失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"语音识别失败: {str(e)}")

