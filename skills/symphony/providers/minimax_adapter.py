# -*- coding: utf-8 -*-
"""
MiniMax 适配器 - 序境系统
===============
兼容 MiniMax Open API v1
支持: chat, embedding, tts, multimodal
"""

import requests
import json

class MiniMaxAdapter:
    """MiniMax API 适配器"""
    
    def __init__(self, api_key: str, group_id: str = None):
        self.API_KEY = api_key
        self.GROUP_ID = group_id
        self.BASE_URL = "https://api.minimax.chat/v1"
        
        self.headers = {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/json"
        }
    
    ENDPOINT_MAP = {
        "chat": "/chat/completions",
        "embedding": "/embeddings",
        "tts": "/text_to_speech",
        "asr": "/speech_to_text",
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
        if self.GROUP_ID and "chat" in url:
            url += f"?GroupId={self.GROUP_ID}"
        
        data = self._build_request_data(model_id, model_type, **kwargs)
        resp = requests.post(url, headers=self.headers, json=data, timeout=60)
        resp.raise_for_status()
        return resp.json()
    
    def _build_request_data(self, model_id, model_type, **kwargs):
        """根据模型类型构建请求参数 - 使用标准OpenAI格式"""
        data = {"model": model_id}
        
        if model_type == "chat":
            # 标准OpenAI格式
            data["messages"] = kwargs.get("messages", [])
            data["max_tokens"] = kwargs.get("max_tokens", 2048)
            data["temperature"] = kwargs.get("temperature", 0.7)
        
        elif model_type == "embedding":
            # MiniMax embedding 接口参数
            data["type"] = kwargs.get("type", "query")
            data["texts"] = kwargs.get("texts", [])
        
        elif model_type == "tts":
            data["text"] = kwargs.get("text", "")
            data["voice_id"] = kwargs.get("voice_id", "default")
        
        elif model_type == "asr":
            data["audio_url"] = kwargs.get("audio_url", "")
        
        return data
    
    def chat_completion(self, messages, **kwargs):
        """便捷的聊天接口"""
        return self.invoke(
            kwargs.get("model", "MiniMax-M2.7"),
            "chat",
            messages=messages,
            **kwargs
        )
    
    def parse_response(self, result):
        """解析标准OpenAI格式响应"""
        if 'choices' in result and len(result['choices']) > 0:
            return {
                'choices': [
                    {
                        'message': {
                            'content': result['choices'][0]['message']['content']
                        }
                    }
                ]
            }
        return result
