# -*- coding: utf-8 -*-
"""
音频处理模块 - Audio Handler

功能：
- 音频信息获取
- 音频格式转换
- TTS语音合成
"""
import os
import io
import base64
import subprocess
from typing import Optional, Dict, Any


class AudioHandler:
    """音频处理器"""
    
    def __init__(self):
        self.ffmpeg_available = self._check_ffmpeg()
    
    def _check_ffmpeg(self) -> bool:
        """检查FFmpeg是否可用"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
            return True
        except:
            return False
    
    def get_audio_info(self, audio_path: str) -> Dict[str, Any]:
        """获取音频信息"""
        if not self.ffmpeg_available:
            return {"error": "FFmpeg not available"}
        
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                audio_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                info = json.loads(result.stdout)
                return {
                    "duration": float(info.get("format", {}).get("duration", 0)),
                    "size": int(info.get("format", {}).get("size", 0)),
                    "format": info.get("format", {}).get("format_name", "")
                }
        except Exception as e:
            return {"error": str(e)}
        
        return {"error": "Failed to get audio info"}
    
    def convert_format(self, input_path: str, output_path: str, target_format: str = "mp3") -> bool:
        """转换音频格式"""
        if not self.ffmpeg_available:
            return False
        
        try:
            cmd = ['ffmpeg', '-i', input_path, '-q:a', '2', output_path]
            result = subprocess.run(cmd, capture_output=True, timeout=60)
            return result.returncode == 0
        except:
            return False
    
    def extract_audio(self, video_path: str, output_path: str) -> bool:
        """从视频提取音频"""
        if not self.ffmpeg_available:
            return False
        
        try:
            cmd = ['ffmpeg', '-i', video_path, '-vn', '-acodec', 'libmp3lame', output_path]
            result = subprocess.run(cmd, capture_output=True, timeout=120)
            return result.returncode == 0
        except:
            return False


class TTSClient:
    """语音合成客户端"""
    
    def __init__(self, api_config: Dict[str, Any] = None):
        self.api_config = api_config or self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """默认配置 - 使用Edge TTS"""
        return {
            "provider": "edge",
            "voice": "zh-CN-XiaoxiaoNeural",
            "rate": "+0%",
            "pitch": "+0Hz"
        }
    
    def speak(self, text: str, output_path: str = None) -> Dict[str, Any]:
        """语音合成"""
        try:
            import edge_tts
            import asyncio
            
            async def generate():
                communicate = edge_tts.Communicate(
                    text,
                    self.api_config.get("voice", "zh-CN-XiaoxiaoNeural"),
                    rate=self.api_config.get("rate", "+0%"),
                    pitch=self.api_config.get("pitch", "+0Hz")
                )
                
                if output_path:
                    await communicate.save(output_path)
                    return {"success": True, "path": output_path}
                else:
                    # 返回音频数据
                    audio_data = b""
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            audio_data += chunk["data"]
                    return {"success": True, "data": audio_data}
            
            return asyncio.run(generate())
            
        except ImportError:
            return {"success": False, "error": "edge-tts not installed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def set_voice(self, voice: str):
        """设置声音"""
        self.api_config["voice"] = voice
    
    def list_voices(self) -> List[Dict]:
        """列出可用声音"""
        try:
            import edge_tts
            import asyncio
            
            async def get_voices():
                voices = await edge_tts.list_voices()
                return [
                    {"name": v["Name"], "locale": v["Locale"], "gender": v["Gender"]}
                    for v in voices if v["Locale"].startswith("zh")
                ]
            
            return asyncio.run(get_voices())
        except:
            return []


# 测试
if __name__ == "__main__":
    handler = AudioHandler()
    print("AudioHandler: OK")
    print("FFmpeg:", handler.ffmpeg_available)
    
    tts = TTSClient()
    print("TTSClient: OK")
