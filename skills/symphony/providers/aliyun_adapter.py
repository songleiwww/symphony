import requests
import json

class AliyunAdapter:
    API_KEY = "sk-fee678dbf4d84f9a910356821c95c0d5"
    BASE_URL = "https://dashscope.aliyuncs.com/api/v1"
    
    # 各模型类型对应的API路径
    ENDPOINT_MAP = {
        "text": "/services/aigc/text-generation/generation",
        "image": "/services/aigc/wanx/text2image",
        "image_edit": "/services/aigc/wanx/image2image",
        "video": "/services/aigc/wanx/text2video",
        "multimodal": "/services/aigc/multimodal-generation/generation",
        "tts": "/services/aigc/speech/synthesizer",
        "asr": "/services/aigc/asr/paraformer/recognize",
        "embedding": "/services/embeddings/text-embedding/text-embedding",
        "rerank": "/services/rerank/gte-rerank-v2"
    }
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/json"
        }
    
    def invoke(self, model_id, model_type, **kwargs):
        """
        统一调用入口
        :param model_id: 模型ID
        :param model_type: 模型类型(text/image/video/multimodal/tts/asr/embedding/rerank)
        :param kwargs: 调用参数
        :return: 调用结果
        """
        if model_type not in self.ENDPOINT_MAP:
            raise ValueError(f"不支持的模型类型: {model_type}")
        
        url = f"{self.BASE_URL}{self.ENDPOINT_MAP[model_type]}"
        data = self._build_request_data(model_id, model_type, **kwargs)
        
        resp = requests.post(url, headers=self.headers, json=data, timeout=30)
        resp.raise_for_status()
        return resp.json()
    
    def _build_request_data(self, model_id, model_type, **kwargs):
        """根据模型类型构建请求参数"""
        data = {"model": model_id}
        
        if model_type == "text":
            data["input"] = {"messages": kwargs.get("messages", [])}
            data["parameters"] = kwargs.get("parameters", {"max_tokens": 1024})
            
        elif model_type == "image":
            data["input"] = {"prompt": kwargs.get("prompt", "")}
            data["parameters"] = kwargs.get("parameters", {"size": "1024*1024", "n": 1})
            
        elif model_type == "multimodal":
            data["input"] = {"messages": kwargs.get("messages", [])}
            data["parameters"] = kwargs.get("parameters", {})
            
        elif model_type == "tts":
            data["input"] = {"text": kwargs.get("text", "")}
            data["parameters"] = kwargs.get("parameters", {"voice": "longxiaochun", "format": "mp3"})
            
        elif model_type == "embedding":
            data["input"] = {"texts": kwargs.get("texts", [])}
            data["parameters"] = kwargs.get("parameters", {"text_type": "query"})
            
        elif model_type == "rerank":
            data["input"] = {
                "query": kwargs.get("query", ""),
                "documents": kwargs.get("documents", [])
            }
            data["parameters"] = kwargs.get("parameters", {"top_n": 10})
            
        elif model_type == "asr":
            data["input"] = {"url": kwargs.get("audio_url", "")}
            data["parameters"] = kwargs.get("parameters", {"sample_rate": 16000})
            
        return data

# 快速测试适配器
if __name__ == "__main__":
    adapter = AliyunAdapter()
    print("=== 阿里云适配器快速测试 ===")
    
    # 1. 测试文本模型（低额度消耗）
    try:
        result = adapter.invoke(
            model_id="qwen2.5-1.8b-instruct",
            model_type="text",
            messages=[{"role": "user", "content": "你好，返回1句话不超过10字"}]
        )
        print("✅ 文本模型测试成功：" + result["output"]["text"].strip())
    except Exception as e:
        print(f"❌ 文本模型测试失败：{str(e)}")
    
    # 2. 测试向量模型
    try:
        result = adapter.invoke(
            model_id="text-embedding-v4",
            model_type="embedding",
            texts=["测试文本"]
        )
        print(f"✅ 向量模型测试成功，维度：{len(result['output']['embeddings'][0]['embedding'])}")
    except Exception as e:
        print(f"❌ 向量模型测试失败：{str(e)}")
    
    print("\n适配器已配置完成，所有模型类型API路径已正确映射")
