"""语音合成服务（TTS）"""
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TTSService:
    """语音合成服务类"""
    
    def __init__(self):
        self.api_key = None  # 第三方TTS API密钥
    
    async def synthesize_speech(self, text: str, language: str = "en-US", voice: Optional[str] = None) -> bytes:
        """合成语音"""
        # 这里可以集成第三方TTS服务，如Azure、Google、讯飞、百度等
        # 目前前端使用Web Speech API，后端保留接口用于未来扩展
        raise NotImplementedError("第三方TTS服务未实现，请使用前端Web Speech API")
    
    def is_available(self) -> bool:
        """检查TTS服务是否可用"""
        return self.api_key is not None


tts_service = TTSService()

