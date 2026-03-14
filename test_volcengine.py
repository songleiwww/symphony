# -*- coding: utf-8 -*-
"""
真正并发模型测试 - 使用有效API Key
"""
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

print("=" * 70)
print("火山引擎API并发测试")
print("=" * 70)

# 使用更新后的配置
TEST_MODEL = "Doubao-Seed-2.0-lite"
TEST_URL = "https://ark.cn-beijing.volces.com/api/coding/v3"
TEST_KEY = "3b922877-3fbe-45d1-a298-53f2231c52e7"

print(f"\n使用模型: {TEST_MODEL}")
print(f"URL: {TEST_URL}")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TEST_KEY}"
}

data = {
    "model": TEST_MODEL,
    "messages": [{"role": "user", "content": "你好，用一句话介绍自己"}],
    "max_tokens": 50
}

# Test 1: 单次调用
print("\n[Test 1] 单次API调用...")
try:
    resp = requests.post(TEST_URL, headers=headers, json=data, timeout=30)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        result = resp.json()
        content = result["choices"][0]["message"]["content"]
        print(f"Response: {content[:150]}")
    else:
        print(f"Error: {resp.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: 并发测试
print("\n" + "=" * 70)
print("[Test 2] 并发API调用 (4线程)")
print("=" * 70)

results = []
errors = []
lock = threading.Lock()

def call_api(thread_id):
    try:
        start = time.time()
        resp = requests.post(TEST_URL, headers=headers, json=data, timeout=30)
        elapsed = time.time() - start
        
        with lock:
            if resp.status_code == 200:
                result = resp.json()
                content = result["choices"][0]["message"]["content"]
                results.append({
                    "thread": thread_id,
                    "time": elapsed,
                    "content": content[:50],
                    "success": True
                })
            else:
                errors.append({
                    "thread": thread_id,
                    "status": resp.status_code,
                    "error": resp.text[:50]
                })
    except Exception as e:
        with lock:
            errors.append({
                "thread": thread_id,
                "error": str(e)[:50]
            })

start_time = time.time()
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(call_api, i) for i in range(4)]
    for f in as_completed(futures):
        try:
            f.result()
        except:
            pass
total_time = time.time() - start_time

print(f"\n并发结果:")
print(f"  成功: {len(results)}")
print(f"  失败: {len(errors)}")
print(f"  总耗时: {total_time:.2f}s")

if results:
    print("\n成功案例:")
    for r in results:
        print(f"  [OK] Thread-{r['thread']}: {r['time']:.2f}s - {r['content']}")

if errors:
    print("\n失败案例:")
    for e in errors:
        print(f"  [FAIL] Thread-{e['thread']}: {e.get('error', 'unknown')}")

print("\n" + "=" * 70)
