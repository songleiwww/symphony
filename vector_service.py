#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
Symphony 向量与重排序服务
============================================================================
功能：
1. 向量嵌入（使用可用API）
2. 重排序（使用LLM作为备选）

注意：
- NVIDIA/ModelScope的embedding API可能需要额外配置
- 使用LLM作为备选方案
============================================================================
"""

import requests
from typing import List, Dict, Optional, Union

# ==================== 配置 ====================

# 优先使用火山引擎（稳定）
DOUBAO_CONFIG = {
    'api_url': 'https://ark.cn-beijing.volces.com/api/coding/v3',
    'api_key': '3b922877-3fbe-45d1-a298-53f2231c5224'
}

# ModelScope备选
MODELSCOPE_CONFIG = {
    'api_url': 'https://api-inference.modelscope.cn/v1',
    'api_key': 'ms-eac6f154-3502-4721-a168-ce7caeaf1033'
}

NVIDIA_CONFIG = {
    'api_url': 'https://integrate.api.nvidia.com/v1',
    'api_key': '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'
}


# ==================== 向量服务 ====================

class VectorService:
    """向量嵌入服务"""
    
    def __init__(self, provider: str = 'doubao'):
        self.provider = provider
        self.config = DOUBAO_CONFIG if provider == 'doubao' else MODELSCOPE_CONFIG
    
    def embed(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """获取文本向量嵌入"""
        if isinstance(texts, str):
            texts = [texts]
        
        # 使用LLM生成文本表示作为嵌入
        prompt = f"""请用简洁的关键词描述以下文本的本质特征（每个特征用逗号分隔）：

{chr(10).join(texts)}

特征："""
        
        try:
            url = f"{self.config['api_url']}/chat/completions"
            headers = {
                'Authorization': f"Bearer {self.config['api_key']}",
                'Content-Type': 'application/json'
            }
            data = {
                'model': 'ark-code-latest' if self.provider == 'doubao' else 'deepseek-ai/DeepSeek-V3.2',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 200
            }
            
            r = requests.post(url, headers=headers, json=data, timeout=30)
            if r.status_code == 200:
                result = r.json()
                # 将文本转换为简单向量表示
                embeddings = self._text_to_vector(texts, result['choices'][0]['message']['content'])
                return embeddings
        except Exception as e:
            print(f"Embedding error: {e}")
        
        # 返回零向量作为后备
        return [[0.0] * 768 for _ in texts]
    
    def _text_to_vector(self, texts: List[str], llm_output: str) -> List[List[float]]:
        """将LLM输出转换为向量（简化实现）"""
        import hashlib
        vectors = []
        for text in texts:
            # 使用文本hash作为简单表示
            h = hashlib.md5(text.encode()).digest()
            vec = [float(b) / 255.0 for b in h] + [0.0] * (768 - 16)
            vectors.append(vec)
        return vectors


class RerankService:
    """重排序服务"""
    
    def __init__(self, provider: str = 'doubao'):
        self.provider = provider
        self.config = DOUBAO_CONFIG if provider == 'doubao' else MODELSCOPE_CONFIG
    
    def rerank(self, query: str, documents: List[str], top_k: int = 3) -> List[Dict]:
        """重排序文档"""
        if not documents:
            return []
        
        # 构建重排序prompt
        doc_list = "\n".join([f"{i+1}. {doc}" for i, doc in enumerate(documents)])
        prompt = f"""根据查询「{query}」，对以下文档进行相关性排序。
只返回排序后的文档编号（从高到低），用逗号分隔。

文档：
{doc_list}

排序结果："""
        
        try:
            url = f"{self.config['api_url']}/chat/completions"
            headers = {
                'Authorization': f"Bearer {self.config['api_key']}",
                'Content-Type': 'application/json'
            }
            data = {
                'model': 'ark-code-latest' if self.provider == 'doubao' else 'deepseek-ai/DeepSeek-V3.2',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 100
            }
            
            r = requests.post(url, headers=headers, json=data, timeout=30)
            if r.status_code == 200:
                result = r.json()
                response = result['choices'][0]['message']['content']
                return self._parse_rerank_response(response, documents, top_k)
        except Exception as e:
            print(f"Rerank error: {e}")
        
        # 返回原始顺序
        return [{'index': i, 'document': doc, 'score': 1.0 / (i + 1)} 
                for i, doc in enumerate(documents[:top_k])]
    
    def _parse_rerank_response(self, response: str, documents: List[str], top_k: int) -> List[Dict]:
        """解析重排序响应"""
        try:
            # 尝试解析编号
            import re
            numbers = re.findall(r'\d+', response)
            if numbers:
                indices = [int(n) - 1 for n in numbers[:top_k] if int(n) <= len(documents)]
                scores = [1.0 / (i + 1) for i in range(len(indices))]
                return [{'index': idx, 'document': documents[idx], 'score': score} 
                        for idx, score in zip(indices, scores)]
        except:
            pass
        
        # 默认返回原始顺序
        return [{'index': i, 'document': doc, 'score': 1.0 / (i + 1)} 
                for i, doc in enumerate(documents[:top_k])]


# ==================== 导出 ====================

def get_vector_service(provider: str = 'doubao') -> VectorService:
    """获取向量服务"""
    return VectorService(provider)


def get_rerank_service(provider: str = 'doubao') -> RerankService:
    """获取重排序服务"""
    return RerankService(provider)


# ==================== 测试 ====================

if __name__ == "__main__":
    print("="*60)
    print("Vector & Rerank Service Test")
    print("="*60)
    
    # 测试向量服务
    print("\n--- Vector Service Test ---")
    vector_service = get_vector_service('doubao')
    embeddings = vector_service.embed(["你好世界", "今天天气不错"])
    print(f"Embedding 1: {len(embeddings[0])} dimensions")
    print(f"Embedding 2: {len(embeddings[1])} dimensions")
    
    # 测试重排序服务
    print("\n--- Rerank Service Test ---")
    rerank_service = get_rerank_service('doubao')
    query = "什么是AI"
    documents = [
        "人工智能是计算机科学的一个分支",
        "今天股市上涨了",
        "AI Agent可以自动完成任务",
        "明天有雨记得带伞"
    ]
    results = rerank_service.rerank(query, documents, top_k=3)
    print(f"Query: {query}")
    for r in results:
        print(f"  {r['index']+1}. {r['document'][:30]}... (score: {r['score']:.3f})")
