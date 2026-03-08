#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
向量引擎效果测试
"""
import requests
import math
import sys
import io
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_KEY = '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'

def get_embedding(text):
    """获取文本的向量嵌入"""
    url = 'https://integrate.api.nvidia.com/v1/embeddings'
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    data = {'model': 'baai/bge-m3', 'input': text, 'encoding_format': 'float'}
    
    start = time.time()
    r = requests.post(url, headers=headers, json=data, timeout=30)
    elapsed = time.time() - start
    
    if r.status_code == 200:
        result = r.json()
        embedding = result['data'][0]['embedding']
        return embedding, elapsed
    return None, 0

def cosine_sim(a, b):
    """计算余弦相似度"""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot / (norm_a * norm_b)

print("="*60)
print("向量引擎效果测试")
print("="*60)
print()

# 测试1: 文本相似度计算
print("【测试1】文本相似度计算")
print("-"*40)

texts = [
    "今天天气很好，阳光明媚",
    "今天是个晴朗的好天气",
    "股市大跌，投资者损失惨重",
    "我喜欢吃苹果",
    "天气晴朗适合出门"
]

query = "天气怎么样"
print(f"查询: {query}")
print()

# 获取查询向量
q_emb, q_time = get_embedding(query)
print(f"查询向量获取: {q_time:.2f}秒, 维度: {len(q_emb)}")
print()

# 计算相似度
results = []
for text in texts:
    t_emb, t_time = get_embedding(text)
    sim = cosine_sim(q_emb, t_emb)
    results.append((text, sim, t_time))
    print(f"  {text[:20]}... 相似度: {sim:.4f}")

# 排序
results.sort(key=lambda x: x[1], reverse=True)
print()
print("排序结果:")
for i, (text, sim, t) in enumerate(results, 1):
    print(f"  {i}. {sim:.4f} | {text}")

print()
print("="*60)

# 测试2: 文档检索
print("【测试2】文档检索")
print("-"*40)

docs = [
    "Python是一种流行的编程语言，广泛用于数据科学和人工智能。",
    "北京是中国的首都，有着悠久的历史和丰富的文化。",
    "机器学习是人工智能的一个分支，通过数据训练模型。",
    "上海是中国最大的城市之一，是重要的经济中心。",
    "深度学习使用神经网络来处理复杂的数据模式。"
]

queries = ["人工智能", "中国城市", "编程语言"]

for query in queries:
    print(f"\n查询: {query}")
    q_emb, _ = get_embedding(query)
    
    doc_scores = []
    for doc in docs:
        d_emb, _ = get_embedding(doc)
        sim = cosine_sim(q_emb, d_emb)
        doc_scores.append((doc[:30], sim))
    
    doc_scores.sort(key=lambda x: x[1], reverse=True)
    print("最相关的文档:")
    for i, (doc, sim) in enumerate(doc_scores[:2], 1):
        print(f"  {i}. [{sim:.4f}] {doc}...")

print()
print("="*60)

# 测试3: 性能统计
print("【测试3】性能统计")
print("-"*40)

test_text = "这是一个测试文本"
total_time = 0
success = 0

for i in range(3):
    emb, t = get_embedding(test_text)
    if emb:
        total_time += t
        success += 1

print(f"测试次数: 3")
print(f"成功次数: {success}")
print(f"平均耗时: {total_time/success:.2f}秒" if success else "失败")
print(f"向量维度: {len(emb)}" if emb else "")

print()
print("="*60)
print("测试完成!")
print("="*60)
