#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
向量嵌入模型调用示例
"""
import requests
import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_KEY = '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'

def get_embedding(text, model='baai/bge-m3'):
    """获取文本的向量嵌入"""
    url = 'https://integrate.api.nvidia.com/v1/embeddings'
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': model,
        'input': text,
        'encoding_format': 'float'
    }
    
    r = requests.post(url, headers=headers, json=data, timeout=30)
    
    if r.status_code == 200:
        result = r.json()
        embedding = result['data'][0]['embedding']
        return embedding
    else:
        print(f'错误: {r.status_code}')
        return None

def cosine_similarity(a, b):
    """计算余弦相似度"""    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    return dot / (norm_a * norm_b)

# 测试示例
print("="*60)
print("向量嵌入模型调用示例")
print("="*60)

# 1. 获取单个文本的嵌入
print("\n1. 获取文本嵌入:")
text1 = "你好，我是交交，青丘女狐"
embedding1 = get_embedding(text1)
if embedding1:
    print(f"   文本: {text1}")
    print(f"   维度: {len(embedding1)}")
    print(f"   前5维: {embedding1[:5]}")

# 2. 获取另一个文本的嵌入
print("\n2. 获取另一个文本嵌入:")
text2 = "青丘是一个美丽的地方"
embedding2 = get_embedding(text2)
if embedding2:
    print(f"   文本: {text2}")
    print(f"   维度: {len(embedding2)}")

# 3. 计算相似度
print("\n3. 计算相似度:")
if embedding1 and embedding2:
    sim = cosine_similarity(embedding1, embedding2)
    print(f"   相似度: {sim:.4f}")

# 4. 向量存储示例
print("\n4. 向量存储示例:")
vector_store = {
    "交交": embedding1,
    "青丘": embedding2
}
print(f"   已存储 {len(vector_store)} 个向量")

print("\n" + "="*60)
print("调用完成")
print("="*60)
