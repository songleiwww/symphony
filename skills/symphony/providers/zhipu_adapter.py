# -*- coding: utf-8 -*-
"""
智谱AI 适配器 - 序境系统
===============
兼容 智谱AI Open API v4
支持: chat, embedding, multimodal
"""

import requests
import json

class ZhipuAdapter:
    """智谱AI API 适配器"""
    
    def __init__(self, api_key: str):
        self.API_KEY = api_key
        self.BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
        
        self.headers = {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/json"
        }
    
    ENDPOINT_MAP = {
        "chat": "/chat/completions",
        "embedding": "/embeddings",
    }
    
    def invoke(self, model_id, model_type, **kwargs):
        """
        统一调用入口
        :param model_id: 模型ID
        :param model_type: 模型类型
        :param kwargs: 调用参数
        :return: 调用结果
        """
        if model_type not in self.ENDPOINT_MAP:
            raise ValueError(f"不支持的模型类型: {model_type}")
        
        url = f"{self.BASE_URL}{self.ENDPOINT_MAP[model_type]}"
        data = self._build_request_data(model_id, model_type, **kwargs)
        
        resp = requests.post(url, headers=self.headers, json=data, timeout=60)
        resp.raise_for_status()
        return resp.json()
    
    def _build_request_data(self, model_id, model_type, **kwargs):
        """根据模型类型构建请求参数"""
        data = {"model": model_id}
        
        if model_type == "chat":
            data["messages"] = kwargs.get("messages", [])
            data["max_tokens"] = kwargs.get("max_tokens", 4096)
            data["temperature"] = kwargs.get("temperature", 0.7)
        
        elif model_type == "embedding":
            data["input"] = kwargs.get("input", [])
        
        return data
    
    def chat_completion(self, messages, **kwargs):
        """便捷的聊天接口"""
        return self.invoke(
            kwargs.get("model", "glm-4"),
            "chat",
            messages=messages,
            **kwargs
        )
