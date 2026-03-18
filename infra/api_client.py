"""
序境内核 - API客户端
"""

import requests
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class APIClient:
    """API调用客户端"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def call(self, api_url: str, api_key: str, model: str, prompt: str, **kwargs) -> Dict:
        """调用API"""
        headers = {"Authorization": f"Bearer {api_key}"}
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            **kwargs
        }
        
        try:
            resp = self.session.post(api_url, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            
            # 提取Token使用 (总则第24条)
            usage = data.get("usage", {})
            return {
                "success": True,
                "content": data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0)
            }
        except Exception as e:
            logger.error(f"API调用失败: {e}")
            return {"success": False, "error": str(e)}


_client: Optional[APIClient] = None


def get_client() -> APIClient:
    global _client
    if _client is None:
        _client = APIClient()
    return _client
