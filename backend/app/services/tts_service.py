"""语音合成服务（TTS）- 使用 Edge-TTS"""
from typing import Optional
import logging
import asyncio
import edge_tts

logger = logging.getLogger(__name__)


class TTSService:
    """语音合成服务类 - 使用 Edge-TTS"""
    
    def __init__(self):
        self._voices_cache = None
        self._voices_cache_lock = asyncio.Lock()
    
    async def get_voices(self):
        """获取可用的语音列表"""
        if self._voices_cache is None:
            async with self._voices_cache_lock:
                if self._voices_cache is None:
                    try:
                        self._voices_cache = await edge_tts.list_voices()
                        logger.info(f"加载了 {len(self._voices_cache)} 个语音")
                    except Exception as e:
                        logger.error(f"获取语音列表失败: {e}")
                        self._voices_cache = []
        return self._voices_cache
    
    async def find_voice(self, language: str = "en-US", voice_name: Optional[str] = None) -> Optional[str]:
        """根据语言和语音名称查找合适的语音
        
        Args:
            language: 语言代码，如 'en-US', 'zh-CN'
            voice_name: 可选的语音名称，如 'en-US-AriaNeural'
        
        Returns:
            语音名称字符串，如果找不到则返回 None
        """
        voices = await self.get_voices()
        
        if voice_name:
            # 如果指定了语音名称，直接查找
            for voice in voices:
                if voice["ShortName"] == voice_name:
                    return voice_name
        
        # 根据语言查找
        lang_code = language.split('-')[0] if '-' in language else language
        
        # 优先查找完全匹配的语言
        for voice in voices:
            if voice["Locale"].startswith(language):
                return voice["ShortName"]
        
        # 查找语言代码匹配的
        for voice in voices:
            if voice["Locale"].startswith(lang_code):
                return voice["ShortName"]
        
        # 默认返回第一个英文语音
        for voice in voices:
            if voice["Locale"].startswith("en"):
                return voice["ShortName"]
        
        # 如果都没有，返回第一个
        if voices:
            return voices[0]["ShortName"]
        
        return None
    
    async def synthesize_speech(
        self, 
        text: str, 
        language: str = "en-US", 
        voice: Optional[str] = None,
        rate: Optional[str] = None,
        pitch: Optional[str] = None
    ) -> bytes:
        """合成语音
        
        Args:
            text: 要合成的文本
            language: 语言代码，如 'en-US', 'zh-CN'
            voice: 可选的语音名称，如 'en-US-AriaNeural'
            rate: 语速，格式如 '+0%', '-20%'，默认 '+0%'
            pitch: 音调，格式如 '+0Hz', '+5Hz'，默认 '+0Hz'
        
        Returns:
            音频字节数据（MP3格式）
        """
        if not text or not text.strip():
            raise ValueError("文本不能为空")
        
        try:
            # 查找合适的语音
            selected_voice = voice
            if not selected_voice:
                selected_voice = await self.find_voice(language, voice)
            
            if not selected_voice:
                raise ValueError(f"找不到适合语言 {language} 的语音")
            
            logger.info(f"使用语音 {selected_voice} 合成文本: {text[:50]}...")
            
            # 构建 communicate 参数
            # Edge-TTS 的 rate 和 pitch 参数直接传递给 communicate
            communicate_params = {
                "text": text,
                "voice": selected_voice
            }
            
            # 添加 rate 和 pitch 参数（如果提供）
            if rate:
                communicate_params["rate"] = rate
            if pitch:
                communicate_params["pitch"] = pitch
            
            # 生成音频
            audio_data = b""
            communicate = edge_tts.Communicate(**communicate_params)
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            logger.info(f"成功合成音频，大小: {len(audio_data)} 字节")
            return audio_data
            
        except Exception as e:
            logger.error(f"语音合成失败: {e}")
            raise
    
    def is_available(self) -> bool:
        """检查TTS服务是否可用"""
        return True  # Edge-TTS 总是可用（不需要 API Key）


tts_service = TTSService()
