# -*- coding: utf-8 -*-
"""
火山引擎API测试 - 限流处理
"""
import requests
import time

print("=" * 70)
print("火山引擎API测试 - 限流处理")
print("=" * 70)

TEST_URL = "https://ark.cn-beijing.volces.com/api/coding/v3"
TEST_KEY = "3b922877-3fbe-45d1-a298-53f2231c5224"
TEST_MODEL = "Doubao-Seed-2.0-lite"

headers = {"Content-Type": "application/json", "Authorization": f"Bearer {TEST_KEY}"}

# 逐个测试，每隔2秒
for i in range(3):
    print(f"\n[Test {i+1}] 间隔2秒调用...")
    data = {
        "model": TEST_MODEL,
        "messages": [{"role": "user", "content": "说一个字：好"}],
        "max_tokens": 10
    }
    try:
        resp = requests.post(TEST_URL, headers=headers, json=data, timeout=30)
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"  Response: {resp.json()['choices'][0]['message']['content']}")
        else:
            print(f"  Error: {resp.text[:100]}")
    except Exception as e:
        print(f"  Exception: {e}")
    
    if i < 2:
        time.sleep(2)

print("\n" + "=" * 70)
