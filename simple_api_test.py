#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单真实模型调用测试
"""

import sys
import json
import requests
import time

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("="*60)
print("简单真实模型调用测试")
print("="*60)

# 从config导入模型配置
from config import MODEL_CHAIN

print(f"\n已加载 {len(MODEL_CHAIN)} 个模型配置")

# 找到第一个可用的模型配置
model = None
for m in MODEL_CHAIN:
    if m.get("enabled", True):
        model = m
        break

if not model:
    print("❌ 没有可用的模型配置")
    exit(1)

print(f"\n测试模型: {model['alias']}")
print(f"提供商: {model['provider']}")
print(f"API: {model['base_url']}")
print(f"Model ID: {model['model_id']}")

# 构建API请求
url = f"{model['base_url']}/chat/completions"
headers = {
    "Authorization": f"Bearer {model['api_key']}",
    "Content-Type": "application/json"
}

data = {
    "model": model["model_id"],
    "messages": [{"role": "user", "content": "你好，请回复'测试成功'"}],
    "max_tokens": 100,
    "temperature": 0.7
}

print("\n正在发送请求...")
start_time = time.time()

try:
    response = requests.post(url, headers=headers, json=data, timeout=30)
    elapsed = time.time() - start_time
    
    print(f"\n响应状态: {response.status_code}")
    print(f"耗时: {elapsed:.2f}s")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ 调用成功!")
        
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            print(f"\n模型回复: {content}")
        
        if "usage" in result:
            usage = result["usage"]
            print(f"\nToken使用:")
            print(f"  Prompt: {usage.get('prompt_tokens', 'N/A')}")
            print(f"  Completion: {usage.get('completion_tokens', 'N/A')}")
            print(f"  Total: {usage.get('total_tokens', 'N/A')}")
    else:
        print(f"\n❌ 调用失败: {response.text[:200]}")
        
except Exception as e:
    print(f"\n❌ 异常: {str(e)}")

print("\n" + "="*60)
