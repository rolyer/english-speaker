"""语音识别服务（STT）"""
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class STTService:
    """语音识别服务类"""
    
    def __init__(self):
        self.api_key = None  # 第三方STT API密钥
    
    async def transcribe_audio(self, audio_data: bytes, language: str = "en-US") -> str:
        """转录音频为文字"""
        # 这里可以集成第三方STT服务，如讯飞、百度、Azure等
        # 目前前端使用Web Speech API，后端保留接口用于未来扩展
        raise NotImplementedError("第三方STT服务未实现，请使用前端Web Speech API")
    
    def is_available(self) -> bool:
        """检查STT服务是否可用"""
        return self.api_key is not None


stt_service = STTService()

