import requests
import json

class NvidiaAdapter:
    """NVIDIA API 适配器"""
    
    BASE_URL = "https://integrate.api.nvidia.com/v1"
    
    ENDPOINT_MAP = {
        "chat": "/chat/completions",
    }
    
    def __init__(self, api_key: str):
        self.API_KEY = api_key
        self.BASE_URL = "https://integrate.api.nvidia.com/v1"
        
        self.headers = {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/json"
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
        stream = kwargs.get("stream", False)
        
        if stream:
            self.headers["Accept"] = "text/event-stream"
        
        payload = {
            "model": model_id,
            "messages": kwargs.get("messages", []),
            "max_tokens": kwargs.get("max_tokens", 4096),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 1.0),
            "stream": stream
        }
        
        if "thinking" in kwargs and kwargs["thinking"]:
            payload["chat_template_kwargs"] = {"thinking": True}
        
        resp = requests.post(url, headers=self.headers, json=payload, timeout=60)
        resp.raise_for_status()
        
        if stream:
            return resp.iter_lines()
        else:
            return resp.json()
    
    def chat_completion(self, messages, **kwargs):
        """便捷的聊天接口"""
        return self.invoke(
            kwargs.get("model", "nvidia/llama-3.1-nemotron-70b-instruct"),
            "chat",
            messages=messages,
            **kwargs
        )
