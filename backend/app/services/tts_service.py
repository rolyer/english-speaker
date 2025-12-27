"""语音合成服务（TTS）- 使用 Edge-TTS"""
from typing import Optional
import logging
import asyncio
import re
import hashlib
import os
from pathlib import Path
import edge_tts

logger = logging.getLogger(__name__)

# 音频缓存目录
AUDIO_CACHE_DIR = Path("./audio_cache")
AUDIO_CACHE_DIR.mkdir(exist_ok=True)


def remove_emojis(text: str) -> str:
    """移除文本中的 emoji 表情
    
    Args:
        text: 原始文本
    
    Returns:
        移除 emoji 后的文本
    """
    # Emoji 的 Unicode 范围（更精确的范围，避免误删中文等字符）
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # 表情符号 (Emoticons)
        "\U0001F300-\U0001F5FF"  # 符号和象形文字 (Misc Symbols and Pictographs)
        "\U0001F680-\U0001F6FF"  # 交通和地图符号 (Transport and Map)
        "\U0001F1E0-\U0001F1FF"  # 旗帜 (Flags)
        "\U0001F900-\U0001F9FF"  # 补充符号和象形文字 (Supplemental Symbols and Pictographs)
        "\U0001FA00-\U0001FA6F"  # 扩展-A (Extended-A)
        "\U0001FA70-\U0001FAFF"  # 符号和象形文字扩展-A (Symbols and Pictographs Extended-A)
        "\U00002600-\U000027BF"  # 杂项符号和装饰符号 (Misc symbols)
        "\U0001F004"             # 麻将牌
        "\U0001F0CF"             # 扑克牌
        "\U0001F170-\U0001F251"  # 封闭字符
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)


def generate_audio_hash(text: str, language: str, voice: Optional[str], rate: Optional[str], pitch: Optional[str]) -> str:
    """生成音频文件的哈希值
    
    Args:
        text: 文本内容
        language: 语言代码
        voice: 语音名称
        rate: 语速
        pitch: 音调
    
    Returns:
        哈希值字符串
    """
    # 组合所有参数生成唯一标识
    content = f"{text}|{language}|{voice or ''}|{rate or ''}|{pitch or ''}"
    return hashlib.md5(content.encode('utf-8')).hexdigest()


class TTSService:
    """语音合成服务类 - 使用 Edge-TTS"""
    
    def __init__(self):
        self._voices_cache = None
        self._voices_cache_lock = asyncio.Lock()
        self.cache_dir = AUDIO_CACHE_DIR
    
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
    
    def get_cache_path(self, audio_hash: str) -> Path:
        """获取缓存文件路径
        
        Args:
            audio_hash: 音频哈希值
        
        Returns:
            缓存文件路径
        """
        return self.cache_dir / f"{audio_hash}.mp3"
    
    def get_cached_audio(self, audio_hash: str) -> Optional[bytes]:
        """从缓存获取音频数据
        
        Args:
            audio_hash: 音频哈希值
        
        Returns:
            音频字节数据，如果不存在则返回 None
        """
        cache_path = self.get_cache_path(audio_hash)
        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    audio_data = f.read()
                logger.info(f"从缓存加载音频: {audio_hash}, 大小: {len(audio_data)} 字节")
                return audio_data
            except Exception as e:
                logger.error(f"读取缓存文件失败: {e}")
                return None
        return None
    
    def save_to_cache(self, audio_hash: str, audio_data: bytes) -> bool:
        """保存音频到缓存
        
        Args:
            audio_hash: 音频哈希值
            audio_data: 音频字节数据
        
        Returns:
            是否保存成功
        """
        cache_path = self.get_cache_path(audio_hash)
        try:
            with open(cache_path, 'wb') as f:
                f.write(audio_data)
            logger.info(f"音频已缓存: {audio_hash}, 大小: {len(audio_data)} 字节")
            return True
        except Exception as e:
            logger.error(f"保存缓存文件失败: {e}")
            return False
    
    async def synthesize_speech(
        self, 
        text: str, 
        language: str = "en-US", 
        voice: Optional[str] = None,
        rate: Optional[str] = None,
        pitch: Optional[str] = None,
        use_cache: bool = True
    ) -> bytes:
        """合成语音
        
        Args:
            text: 要合成的文本
            language: 语言代码，如 'en-US', 'zh-CN'
            voice: 可选的语音名称，如 'en-US-AriaNeural'
            rate: 语速，格式如 '+0%', '-20%'，默认 '+0%'
            pitch: 音调，格式如 '+0Hz', '+5Hz'，默认 '+0Hz'
            use_cache: 是否使用缓存，默认 True
        
        Returns:
            音频字节数据（MP3格式）
        """
        if not text or not text.strip():
            raise ValueError("文本不能为空")
        
        try:
            # 移除 emoji 表情
            cleaned_text = remove_emojis(text).strip()
            
            # 如果清理后文本为空，返回错误
            if not cleaned_text:
                raise ValueError("文本清理后为空（可能只包含 emoji）")
            
            # 查找合适的语音
            selected_voice = voice
            if not selected_voice:
                selected_voice = await self.find_voice(language, voice)
            
            if not selected_voice:
                raise ValueError(f"找不到适合语言 {language} 的语音")
            
            # 生成音频哈希
            audio_hash = generate_audio_hash(cleaned_text, language, selected_voice, rate, pitch)
            
            # 检查缓存
            if use_cache:
                cached_audio = self.get_cached_audio(audio_hash)
                if cached_audio:
                    return cached_audio
            
            logger.info(f"使用语音 {selected_voice} 合成文本: {cleaned_text[:50]}...")
            
            # 构建 communicate 参数
            # Edge-TTS 的 rate 和 pitch 参数直接传递给 communicate
            communicate_params = {
                "text": cleaned_text,  # 使用清理后的文本
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
            
            # 保存到缓存
            if use_cache and audio_data:
                self.save_to_cache(audio_hash, audio_data)
            
            return audio_data
            
        except Exception as e:
            logger.error(f"语音合成失败: {e}")
            raise
    
    def clear_cache(self, max_age_days: Optional[int] = None) -> int:
        """清理缓存文件
        
        Args:
            max_age_days: 删除超过指定天数的缓存文件，None 表示删除所有
        
        Returns:
            删除的文件数量
        """
        import time
        
        deleted_count = 0
        try:
            for cache_file in self.cache_dir.glob("*.mp3"):
                should_delete = False
                
                if max_age_days is None:
                    should_delete = True
                else:
                    # 检查文件年龄
                    file_age = time.time() - cache_file.stat().st_mtime
                    if file_age > max_age_days * 86400:  # 转换为秒
                        should_delete = True
                
                if should_delete:
                    try:
                        cache_file.unlink()
                        deleted_count += 1
                    except Exception as e:
                        logger.error(f"删除缓存文件失败 {cache_file}: {e}")
            
            logger.info(f"清理了 {deleted_count} 个缓存文件")
            return deleted_count
        except Exception as e:
            logger.error(f"清理缓存失败: {e}")
            return deleted_count
    
    def get_cache_stats(self) -> dict:
        """获取缓存统计信息
        
        Returns:
            缓存统计信息字典
        """
        try:
            cache_files = list(self.cache_dir.glob("*.mp3"))
            total_size = sum(f.stat().st_size for f in cache_files)
            
            return {
                "count": len(cache_files),
                "total_size": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "cache_dir": str(self.cache_dir)
            }
        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
            return {
                "count": 0,
                "total_size": 0,
                "total_size_mb": 0,
                "cache_dir": str(self.cache_dir)
            }
    
    def is_available(self) -> bool:
        """检查TTS服务是否可用"""
        return True  # Edge-TTS 总是可用（不需要 API Key）


tts_service = TTSService()
