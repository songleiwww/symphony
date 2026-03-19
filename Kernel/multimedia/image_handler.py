# -*- coding: utf-8 -*-
"""
图像处理模块 - Image Handler

功能：
- 图像格式转换
- 图像压缩
- 缩略图生成
- 图像元数据提取
"""
import os
import io
import json
import base64
from typing import Optional, Dict, Any, Tuple
from PIL import Image


class ImageHandler:
    """图像处理器"""
    
    SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff']
    
    def __init__(self):
        pass
    
    def get_image_info(self, image_data: bytes) -> Dict[str, Any]:
        """获取图像信息"""
        try:
            img = Image.open(io.BytesIO(image_data))
            return {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
                "size_bytes": len(image_data)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def resize(self, image_data: bytes, width: int, height: int, keep_aspect: bool = True) -> bytes:
        """调整图像大小"""
        img = Image.open(io.BytesIO(image_data))
        
        if keep_aspect:
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
        else:
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        output = io.BytesIO()
        img.save(output, format=img.format or 'PNG')
        return output.getvalue()
    
    def create_thumbnail(self, image_data: bytes, max_size: int = 256) -> bytes:
        """创建缩略图"""
        img = Image.open(io.BytesIO(image_data))
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        output = io.BytesIO()
        img.save(output, format='PNG')
        return output.getvalue()
    
    def compress(self, image_data: bytes, quality: int = 85, format: str = None) -> bytes:
        """压缩图像"""
        img = Image.open(io.BytesIO(image_data))
        
        output = io.BytesIO()
        img.save(output, format=format or img.format or 'JPEG', quality=quality)
        return output.getvalue()
    
    def convert_format(self, image_data: bytes, target_format: str) -> bytes:
        """转换图像格式"""
        img = Image.open(io.BytesIO(image_data))
        
        # 转换模式
        if target_format.upper() in ['JPEG', 'JPG'] and img.mode in ['RGBA', 'LA', 'P']:
            img = img.convert('RGB')
        
        output = io.BytesIO()
        img.save(output, format=target_format.upper())
        return output.getvalue()
    
    def to_base64(self, image_data: bytes, format: str = None) -> str:
        """转换为Base64"""
        return base64.b64encode(image_data).decode('utf-8')
    
    def from_base64(self, base64_str: str) -> bytes:
        """从Base64解码"""
        return base64.b64decode(base64_str)
    
    def crop(self, image_data: bytes, x: int, y: int, width: int, height: int) -> bytes:
        """裁剪图像"""
        img = Image.open(io.BytesIO(image_data))
        img = img.crop((x, y, x + width, y + height))
        
        output = io.BytesIO()
        img.save(output, format=img.format or 'PNG')
        return output.getvalue()
    
    def rotate(self, image_data: bytes, angle: float) -> bytes:
        """旋转图像"""
        img = Image.open(io.BytesIO(image_data))
        img = img.rotate(angle, expand=True)
        
        output = io.BytesIO()
        img.save(output, format=img.format or 'PNG')
        return output.getvalue()


class ImageAnalyzer:
    """图像分析器（简化版）"""
    
    def __init__(self):
        pass
    
    def analyze(self, image_data: bytes) -> Dict[str, Any]:
        """分析图像"""
        try:
            img = Image.open(io.BytesIO(image_data))
            
            # 基础分析
            result = {
                "width": img.width,
                "height": img.height,
                "aspect_ratio": round(img.width / img.height, 2) if img.height > 0 else 0,
                "format": img.format,
                "mode": img.mode,
                "size_kb": round(len(image_data) / 1024, 2),
                "has_alpha": img.mode in ('RGBA', 'LA'),
                "is_animated": getattr(img, 'is_animated', False)
            }
            
            # 颜色分析
            if img.mode in ('RGB', 'RGBA'):
                result["colors"] = self._analyze_colors(img)
            
            return result
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_colors(self, img: Image.Image) -> Dict[str, Any]:
        """分析颜色"""
        img_small = img.copy()
        img_small.thumbnail((100, 100))
        
        # 简化分析：获取主要颜色
        colors = img_small.getcolors(maxcolors=256)
        if colors:
            colors = sorted(colors, key=lambda x: x[0], reverse=True)[:5]
            return {
                "dominant": [{"color": c[1], "count": c[0]} for c in colors]
            }
        return {}


if __name__ == "__main__":
    # 测试
    handler = ImageHandler()
    print("ImageHandler: OK")
    
    analyzer = ImageAnalyzer()
    print("ImageAnalyzer: OK")
    
    # 创建测试图像
    img = Image.new('RGB', (100, 100), color='red')
    output = io.BytesIO()
    img.save(output, format='JPEG')
    test_data = output.getvalue()
    
    # 测试分析
    info = handler.get_image_info(test_data)
    print("Image info:", info)
    
    analysis = analyzer.analyze(test_data)
    print("Analysis:", analysis)
