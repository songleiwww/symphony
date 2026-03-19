# -*- coding: utf-8 -*-
"""
视觉理解客户端 - Vision Client

功能：
- 对接GLM-4 Vision等视觉模型
- 图像理解与描述
- 多模态对话
"""
import json
import base64
import requests
from typing import Optional, Dict, Any, List


class VisionClient:
    """视觉理解客户端"""
    
    def __init__(self, api_config: Dict[str, Any] = None):
        self.api_config = api_config or self._default_config()
        self.client = None
    
    def _default_config(self) -> Dict[str, Any]:
        """默认配置 - 使用智谱GLM-4V-Flash"""
        return {
            "provider": "zhipu",
            "model": "glm-4v-flash",
            "api_key": "83e29cfa875a48d99064a8d0c6977a7f.XuH7V1qwfToXD7es",
            "api_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        }
    
    def set_config(self, config: Dict[str, Any]):
        """设置配置"""
        self.api_config.update(config)
    
    def encode_image(self, image_data: bytes) -> str:
        """编码图像为base64"""
        return base64.b64encode(image_data).decode('utf-8')
    
    def describe_image(self, image_data: bytes, prompt: str = None) -> Dict[str, Any]:
        """描述图像内容"""
        if prompt is None:
            prompt = "请详细描述这张图片的内容"
        
        image_base64 = self.encode_image(image_data)
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                    }
                ]
            }
        ]
        
        return self._call_api(messages)
    
    def analyze_image(self, image_data: bytes, analysis_type: str = "general") -> Dict[str, Any]:
        """分析图像"""
        prompts = {
            "general": "请详细描述这张图片的内容，包括场景、人物、物体、颜色等要素。",
            "text": "请提取这张图片中的所有文字内容。",
            "object": "请列出这张图片中的所有物体和它们的位置。",
            "ocr": "请进行OCR识别，提取图片中的所有文字。",
            "chart": "请分析这张图表，描述数据趋势和关键信息。"
        }
        
        prompt = prompts.get(analysis_type, prompts["general"])
        return self.describe_image(image_data, prompt)
    
    def multimodal_conversation(self, image_data: bytes, messages: List[Dict]) -> Dict[str, Any]:
        """多模态对话"""
        image_base64 = self.encode_image(image_data)
        
        # 添加图像到第一条用户消息
        if messages and messages[0].get("role") == "user":
            messages[0]["content"] = [
                {"type": "text", "text": messages[0].get("content", "")},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                }
            ]
        
        return self._call_api(messages)
    
    def _call_api(self, messages: List[Dict]) -> Dict[str, Any]:
        """调用API"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_config.get('api_key', '')}"
            }
            
            payload = {
                "model": self.api_config.get("model", "glm-4v-flash"),
                "messages": messages,
                "max_tokens": 1024
            }
            
            response = requests.post(
                self.api_config.get("api_url"),
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "content": result.get("choices", [{}])[0].get("message", {}).get("content", ""),
                    "usage": result.get("usage", {})
                }
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}",
                    "detail": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class VisionManager:
    """视觉理解管理器"""
    
    def __init__(self):
        self.clients = {}
        self.default_client = None
    
    def register_client(self, name: str, client: VisionClient):
        """注册视觉客户端"""
        self.clients[name] = client
        if self.default_client is None:
            self.default_client = name
    
    def set_default(self, name: str):
        """设置默认客户端"""
        if name in self.clients:
            self.default_client = name
    
    def describe(self, image_data: bytes, prompt: str = None, client_name: str = None) -> Dict[str, Any]:
        """描述图像"""
        name = client_name or self.default_client
        if name and name in self.clients:
            return self.clients[name].describe_image(image_data, prompt)
        return {"success": False, "error": "No client available"}
    
    def analyze(self, image_data: bytes, analysis_type: str = "general", client_name: str = None) -> Dict[str, Any]:
        """分析图像"""
        name = client_name or self.default_client
        if name and name in self.clients:
            return self.clients[name].analyze_image(image_data, analysis_type)
        return {"success": False, "error": "No client available"}


# 便捷函数
def create_vision_client(provider: str = "volcengine", **kwargs) -> VisionClient:
    """创建视觉客户端"""
    config = {"provider": provider}
    config.update(kwargs)
    return VisionClient(config)


if __name__ == "__main__":
    # 测试
    client = VisionClient()
    print("VisionClient: OK")
    
    manager = VisionManager()
    print("VisionManager: OK")
