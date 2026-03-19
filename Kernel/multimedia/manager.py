# -*- coding: utf-8 -*-
"""
多媒体管理器 - Multimedia Manager

统一调度所有多媒体功能，提供简单API接口
"""
import os
import io
import base64
from typing import Optional, Dict, Any, Union
from PIL import Image

from .media_storage import MediaStorage, MediaUploader
from .image_handler import ImageHandler, ImageAnalyzer
from .vision_client import VisionClient, VisionManager
from .video_handler import VideoHandler, VideoAnalyzer
from .audio_handler import AudioHandler, TTSClient


class MultimediaManager:
    """
    多媒体管理器
    
    统一调度所有多媒体功能，提供简单API接口
    """
    
    def __init__(self):
        # 初始化各模块
        self.storage = MediaStorage()
        self.uploader = MediaUploader(self.storage)
        self.image_handler = ImageHandler()
        self.image_analyzer = ImageAnalyzer()
        self.vision_client = VisionClient()
        self.vision_manager = VisionManager()
        self.vision_manager.register_client('glm4v', self.vision_client)
        
        self.video_handler = VideoHandler()
        self.video_analyzer = VideoAnalyzer(self.vision_client)
        
        self.audio_handler = AudioHandler()
        self.tts_client = TTSClient()
        
        # 统计
        self.stats = {
            "images_processed": 0,
            "videos_processed": 0,
            "audio_processed": 0,
            "tts_requests": 0
        }
    
    # ========== 图像处理 ==========
    
    def process_image(self, image_data: bytes, operation: str = "analyze", **kwargs) -> Dict[str, Any]:
        """
        处理图像
        
        参数:
            image_data: 图像数据
            operation: 操作类型 (analyze/resize/compress/crop)
            **kwargs: 操作参数
        
        返回:
            处理结果
        """
        try:
            if operation == "analyze":
                # 分析图像
                analysis = self.image_analyzer.analyze(image_data)
                
                # 视觉理解
                vision_result = self.vision_client.analyze_image(
                    image_data, 
                    analysis_type=kwargs.get("analysis_type", "general")
                )
                
                self.stats["images_processed"] += 1
                
                return {
                    "success": True,
                    "image_info": analysis,
                    "vision": vision_result
                }
            
            elif operation == "resize":
                width = kwargs.get("width", 800)
                height = kwargs.get("height", 600)
                result = self.image_handler.resize(image_data, width, height)
                self.stats["images_processed"] += 1
                return {"success": True, "data": result}
            
            elif operation == "compress":
                quality = kwargs.get("quality", 85)
                result = self.image_handler.compress(image_data, quality)
                self.stats["images_processed"] += 1
                return {"success": True, "data": result}
            
            elif operation == "thumbnail":
                max_size = kwargs.get("max_size", 256)
                result = self.image_handler.create_thumbnail(image_data, max_size)
                self.stats["images_processed"] += 1
                return {"success": True, "data": result}
            
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def describe_image(self, image_data: bytes, prompt: str = None) -> Dict[str, Any]:
        """描述图像"""
        try:
            result = self.vision_client.describe_image(image_data, prompt)
            self.stats["images_processed"] += 1
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def ocr_image(self, image_data: bytes) -> Dict[str, Any]:
        """OCR识别"""
        return self.vision_client.analyze_image(image_data, "ocr")
    
    # ========== 视频处理 ==========
    
    def process_video(self, video_path: str, operation: str = "analyze", **kwargs) -> Dict[str, Any]:
        """
        处理视频
        
        参数:
            video_path: 视频文件路径
            operation: 操作类型 (analyze/extract_frames/thumbnail)
        """
        try:
            if operation == "analyze":
                result = self.video_analyzer.analyze_video(video_path)
                self.stats["videos_processed"] += 1
                return result
            
            elif operation == "extract_frames":
                count = kwargs.get("count", 5)
                frames = self.video_handler.extract_frames(video_path, count)
                return {"success": True, "frames": len(frames)}
            
            elif operation == "thumbnail":
                thumb = self.video_handler.get_thumbnail(video_path)
                if thumb:
                    return {"success": True, "data": thumb}
                return {"success": False, "error": "Failed to extract thumbnail"}
            
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ========== 音频处理 ==========
    
    def text_to_speech(self, text: str, output_path: str = None, **kwargs) -> Dict[str, Any]:
        """
        文字转语音
        
        参数:
            text: 要转换的文字
            output_path: 输出文件路径
            voice: 声音选项
        """
        try:
            if output_path:
                voice = kwargs.get("voice", "zh-CN-XiaoxiaoNeural")
                self.tts_client.set_voice(voice)
                result = self.tts_client.speak(text, output_path)
                self.stats["tts_requests"] += 1
                return result
            else:
                return {"success": False, "error": "output_path required"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def speech_to_text(self, audio_path: str) -> Dict[str, Any]:
        """语音转文字（待实现）"""
        return {"success": False, "error": "Not implemented"}
    
    # ========== 文件处理 ==========
    
    def upload_file(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """上传文件"""
        return self.uploader.upload(file_data, filename)
    
    def upload_base64(self, base64_data: str, filename: str = None) -> Dict[str, Any]:
        """上传Base64文件"""
        return self.uploader.upload_base64(base64_data, filename)
    
    # ========== 工具 ==========
    
    def image_to_base64(self, image_data: bytes) -> str:
        """图像转Base64"""
        return base64.b64encode(image_data).decode('utf-8')
    
    def base64_to_image(self, base64_str: bytes) -> bytes:
        """Base64转图像"""
        return base64.b64decode(base64_str)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()


# 全局实例
_multimedia_manager = None

def get_manager() -> MultimediaManager:
    """获取全局多媒体管理器"""
    global _multimedia_manager
    if _multimedia_manager is None:
        _multimedia_manager = MultimediaManager()
    return _multimedia_manager


# 便捷函数
def process_image(image_data: bytes, operation: str = "analyze", **kwargs) -> Dict[str, Any]:
    """处理图像"""
    return get_manager().process_image(image_data, operation, **kwargs)

def describe_image(image_data: bytes, prompt: str = None) -> Dict[str, Any]:
    """描述图像"""
    return get_manager().describe_image(image_data, prompt)

def ocr_image(image_data: bytes) -> Dict[str, Any]:
    """OCR识别"""
    return get_manager().ocr_image(image_data)

def text_to_speech(text: str, output_path: str = None, **kwargs) -> Dict[str, Any]:
    """文字转语音"""
    return get_manager().text_to_speech(text, output_path, **kwargs)


if __name__ == "__main__":
    # 测试
    manager = MultimediaManager()
    print("MultimediaManager: OK")
    print("Stats:", manager.get_stats())
