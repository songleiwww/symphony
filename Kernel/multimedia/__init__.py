# -*- coding: utf-8 -*-
"""
多媒体处理模块 - Multimedia Module

序境系统多媒体处理核心模块

功能：
- 图像处理（理解、生成）
- 视频处理（理解、生成）
- 音频处理（识别、合成）
- 多模态融合

模块结构：
- media_storage: 媒体存储管理
- image_handler: 图像处理
- vision_client: 视觉理解
- video_handler: 视频处理
- audio_handler: 音频处理
- manager: 统一管理器
"""
from .media_storage import MediaStorage, MediaUploader
from .image_handler import ImageHandler, ImageAnalyzer
from .vision_client import VisionClient, VisionManager
from .video_handler import VideoHandler, VideoAnalyzer
from .audio_handler import AudioHandler, TTSClient
from .manager import MultimediaManager, get_manager

__all__ = [
    "MediaStorage",
    "MediaUploader", 
    "ImageHandler",
    "ImageAnalyzer",
    "VisionClient",
    "VisionManager",
    "VideoHandler",
    "VideoAnalyzer",
    "AudioHandler",
    "TTSClient",
    "MultimediaManager",
    "get_manager"
]
