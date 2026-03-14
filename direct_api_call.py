#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接调用真实模型API
"""

import sys
import io
import json
import time
import requests

# 修复Windows编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("=" * 80)
print("🎯 直接调用真实模型API")
print("=" * 80)

# 1. cherry-doubao/ark-code-latest
print("\n[1] 调用 cherry-doubao/ark-code-latest...")
try:
    start = time.time()
    response = requests.post(
        "https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions",
        headers={
            "Authorization": "Bearer 3b922877-3fbe-45d1-a298-53f2231c5224",
            "Content-Type": "application/json"
        },
        json={
            "model": "ark-code-latest",
            "messages": [{"role": "user", "content": "你好，我是林思远，系统架构师。请从系统架构角度，对Symphony v0.7.0的发展方向给出建议。"}],
            "max_tokens": 500
        },
        timeout=30
    )
    latency = time.time() - start
    result = response.json()
    print(f"   ✅ 成功！")
    print(f"   延迟: {latency:.2f}秒")
    print(f"   响应: {result['choices'][0]['message']['content']}")
    print(f"   Token: {result['usage']['total_tokens']}")
except Exception as e:
    print(f"   ❌ 失败: {e}")

# 2. cherry-doubao/deepseek-v3.2
print("\n[2] 调用 cherry-doubao/deepseek-v3.2...")
try:
    start = time.time()
    response = requests.post(
        "https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions",
        headers={
            "Authorization": "Bearer 3b922877-3fbe-45d1-a298-53f2231c5224",
            "Content-Type": "application/json"
        },
        json={
            "model": "deepseek-v3.2",
            "messages": [{"role": "user", "content": "你好，我是陈美琪，用户体验设计师。请从用户体验角度，对Symphony v0.7.0的发展方向给出建议。"}],
            "max_tokens": 500
        },
        timeout=30
    )
    latency = time.time() - start
    result = response.json()
    print(f"   ✅ 成功！")
    print(f"   延迟: {latency:.2f}秒")
    print(f"   响应: {result['choices'][0]['message']['content']}")
    print(f"   Token: {result['usage']['total_tokens']}")
except Exception as e:
    print(f"   ❌ 失败: {e}")

print("\n" + "=" * 80)
print("✅ 完成！")
print("=" * 80)
