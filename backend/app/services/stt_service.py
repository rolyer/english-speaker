"""语音识别服务（STT）- 使用本地 Whisper 模型"""
from typing import Optional, Dict
import logging
import tempfile
import os
import asyncio
import math
from pathlib import Path

logger = logging.getLogger(__name__)

# 全局 Whisper 模型实例
_whisper_model = None


def get_whisper_model():
    """获取或初始化 Whisper 模型（懒加载）"""
    global _whisper_model
    if _whisper_model is None:
        try:
            import whisper
            # 使用 base 模型（速度和准确度的平衡）
            # 可选模型: tiny, base, small, medium, large
            # tiny: 最快但准确度较低
            # base: 速度和准确度平衡（推荐）
            # small/medium/large: 更准确但更慢
            logger.info("正在加载 Whisper 模型...")
            _whisper_model = whisper.load_model("base")
            logger.info("Whisper 模型加载成功")
        except ImportError:
            logger.error("whisper 包未安装，请运行: pip install openai-whisper")
            raise ImportError("请安装 openai-whisper: pip install openai-whisper")
        except Exception as e:
            logger.error(f"加载 Whisper 模型失败: {str(e)}")
            raise
    return _whisper_model


class STTService:
    """语音识别服务类 - 使用本地 Whisper 模型"""
    
    def __init__(self):
        self.model = None
    
    async def transcribe_with_confidence(self, audio_data: bytes, language: str = "en") -> Dict:
        """
        使用本地 Whisper 模型转录音频为文字，并返回置信度
        
        Args:
            audio_data: 音频数据（WebM/OGG/MP3/WAV 格式）
            language: 语言代码（如 "en", "zh"）
        
        Returns:
            包含 text, confidence, low_confidence, language 的字典
        """
        try:
            # 获取模型
            model = get_whisper_model()
            
            # 创建临时文件保存音频
            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            try:
                # 在线程池中运行 Whisper（避免阻塞事件循环）
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: model.transcribe(
                        temp_path,
                        language=language,
                        fp16=False,  # CPU 模式
                        verbose=False
                    )
                )
                
                text = result.get('text', '').strip()
                
                # 基于 avg_logprob 计算置信度（0..1）
                segments = result.get("segments") or []
                conf = None
                if segments:
                    total_w = 0.0
                    total_c = 0.0
                    for s in segments:
                        avg_logprob = s.get("avg_logprob")
                        if avg_logprob is None:
                            continue
                        # 按 segment 时长加权
                        dur = float(s.get("end", 0.0)) - float(s.get("start", 0.0))
                        w = max(dur, 0.01)
                        c = math.exp(float(avg_logprob))
                        c = max(0.0, min(1.0, c))
                        total_w += w
                        total_c += w * c
                    if total_w > 0:
                        conf = total_c / total_w
                
                # 阈值：可后续做成配置项
                low_confidence = (conf is not None) and (conf < 0.55)
                
                conf_str = f"{conf:.2f}" if conf is not None else "N/A"
                logger.info(f"语音识别成功: {text[:50]}... (confidence: {conf_str})")
                
                return {
                    "text": text,
                    "confidence": conf,
                    "low_confidence": low_confidence,
                    "language": language
                }
                
            finally:
                # 删除临时文件
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
        except ImportError as e:
            logger.error(f"Whisper 未安装: {str(e)}")
            raise Exception("语音识别服务未配置，请安装 openai-whisper")
        except Exception as e:
            logger.error(f"语音识别失败: {str(e)}")
            raise Exception(f"语音识别失败: {str(e)}")
    
    async def transcribe_audio(self, audio_data: bytes, language: str = "en") -> str:
        """
        使用本地 Whisper 模型转录音频为文字（保持向后兼容）
        
        Args:
            audio_data: 音频数据（WebM/OGG/MP3/WAV 格式）
            language: 语言代码（如 "en", "zh"）
        
        Returns:
            转录的文本
        """
        result = await self.transcribe_with_confidence(audio_data, language)
        return result["text"]
    
    def is_available(self) -> bool:
        """检查STT服务是否可用"""
        try:
            import whisper
            return True
        except ImportError:
            return False


stt_service = STTService()

