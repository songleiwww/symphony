# -*- coding: utf-8 -*-
"""
NVIDIA API测试 - 尝试多个模型
"""
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

print("=" * 70)
print("NVIDIA API测试 - 多个模型")
print("=" * 70)

TEST_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
TEST_KEY = "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"

# 尝试不同模型
models = [
    "nvidia/llama-3.1-nemotron-70b-instruct",
    "mistralai/mixtral-8x7b-instruct-v0.1", 
    "google/gemma-2-27b-it",
    "meta/llama-3.1-70b-instruct"
]

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TEST_KEY}"
}

# Test: 尝试不同模型
for model in models:
    print(f"\n测试模型: {model}")
    data = {
        "model": model,
        "messages": [{"role": "user", "content": "说一个字：好"}],
        "max_tokens": 10
    }
    try:
        resp = requests.post(TEST_URL, headers=headers, json=data, timeout=30)
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            result = resp.json()
            content = result["choices"][0]["message"]["content"]
            print(f"  Response: {content}")
            break
        else:
            print(f"  Error: {resp.text[:80]}")
    except Exception as e:
        print(f"  Exception: {str(e)[:50]}")

print("\n" + "=" * 70)
