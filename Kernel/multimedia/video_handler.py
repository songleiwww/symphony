# -*- coding: utf-8 -*-
"""
视频处理模块 - Video Handler

功能：
- 视频信息获取
- 视频截图
- 视频理解（调用视觉模型）
"""
import os
import io
import json
import base64
import subprocess
from typing import Optional, Dict, Any, List
from PIL import Image


class VideoHandler:
    """视频处理器"""
    
    def __init__(self):
        self.ffmpeg_available = self._check_ffmpeg()
    
    def _check_ffmpeg(self) -> bool:
        """检查FFmpeg是否可用"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
            return True
        except:
            return False
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """获取视频信息"""
        if not self.ffmpeg_available:
            return {"error": "FFmpeg not available"}
        
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                info = json.loads(result.stdout)
                return {
                    "duration": float(info.get("format", {}).get("duration", 0)),
                    "size": int(info.get("format", {}).get("size", 0)),
                    "format": info.get("format", {}).get("format_name", ""),
                    "streams": len(info.get("streams", []))
                }
        except Exception as e:
            return {"error": str(e)}
        
        return {"error": "Failed to get video info"}
    
    def extract_frame(self, video_path: str, timestamp: float = 0) -> Optional[bytes]:
        """提取视频帧"""
        if not self.ffmpeg_available:
            return None
        
        try:
            cmd = [
                'ffmpeg',
                '-ss', str(timestamp),
                '-i', video_path,
                '-vframes', '1',
                '-f', 'image2pipe',
                '-vcodec', 'png',
                '-'
            ]
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            
            if result.returncode == 0 and len(result.stdout) > 0:
                return result.stdout
        except:
            pass
        
        return None
    
    def extract_frames(self, video_path: str, count: int = 5) -> List[bytes]:
        """提取多个视频帧"""
        frames = []
        
        # 获取视频时长
        info = self.get_video_info(video_path)
        duration = info.get("duration", 0)
        
        if duration <= 0:
            return frames
        
        # 均匀提取帧
        timestamps = [duration * i / count for i in range(count)]
        
        for ts in timestamps:
            frame = self.extract_frame(video_path, ts)
            if frame:
                frames.append(frame)
        
        return frames
    
    def get_thumbnail(self, video_path: str) -> Optional[bytes]:
        """获取视频缩略图"""
        return self.extract_frame(video_path, 1.0)


class VideoAnalyzer:
    """视频分析器"""
    
    def __init__(self, vision_client=None):
        self.vision_client = vision_client
        self.video_handler = VideoHandler()
    
    def set_vision_client(self, client):
        """设置视觉客户端"""
        self.vision_client = client
    
    def analyze_video(self, video_path: str, analysis_type: str = "general") -> Dict[str, Any]:
        """分析视频"""
        # 提取关键帧
        frames = self.video_handler.extract_frames(video_path, count=3)
        
        if not frames:
            return {"success": False, "error": "Failed to extract frames"}
        
        # 分析第一帧作为代表
        if self.vision_client:
            result = self.vision_client.analyze_image(frames[0], analysis_type)
            return {
                "success": True,
                "frame_count": len(frames),
                "analysis": result
            }
        
        return {
            "success": True,
            "frame_count": len(frames),
            "message": "Vision client not set, frames extracted"
        }
    
    def summarize_video(self, video_path: str, prompt: str = None) -> Dict[str, Any]:
        """视频摘要"""
        if prompt is None:
            prompt = "请描述这个视频的主要内容"
        
        frames = self.video_handler.extract_frames(video_path, count=5)
        
        if not frames:
            return {"success": False, "error": "No frames extracted"}
        
        if not self.vision_client:
            return {"success": False, "error": "Vision client not set"}
        
        results = []
        for i, frame in enumerate(frames):
            result = self.vision_client.describe_image(frame, f"{prompt} (第{i+1}帧)")
            results.append(result)
        
        return {
            "success": True,
            "frame_count": len(frames),
            "results": results
        }


# 简单测试
if __name__ == "__main__":
    handler = VideoHandler()
    print("VideoHandler: OK")
    print("FFmpeg available:", handler.ffmpeg_available)
    
    analyzer = VideoAnalyzer()
    print("VideoAnalyzer: OK")
