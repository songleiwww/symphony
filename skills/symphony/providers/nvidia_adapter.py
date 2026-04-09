import requests
import json

class NvidiaAdapter:
    BASE_URL = "https://integrate.api.nvidia.com/v1"
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def invoke(self, model_id, **kwargs):
        """
        调用英伟达模型
        :param model_id: 模型ID
        :param kwargs: 调用参数：messages, stream, max_tokens等
        :return: 调用结果
        """
        url = f"{self.BASE_URL}/chat/completions"
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
