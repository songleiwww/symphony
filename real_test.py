# -*- coding: utf-8 -*-
"""
真正并发模型测试 - 直接API调用验证
"""
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

# 测试配置
TEST_MODEL = "Doubao-Seed-2.0-lite"
TEST_URL = "https://ark.cn-beijing.volces.com/api/coding/v3"
TEST_KEY = "3b922877-3fbe-45d1-a"  # 部分key

print("=" * 70)
print("真正并发模型API测试")
print("=" * 70)

# Test 1: 单次调用
print("\n[Test 1] 单次API调用...")
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TEST_KEY}"
}

data = {
    "model": TEST_MODEL,
    "messages": [{"role": "user", "content": "你好"}],
    "max_tokens": 100
}

try:
    resp = requests.post(TEST_URL, headers=headers, json=data, timeout=30)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: 并发调用
print("\n" + "=" * 70)
print("[Test 2] 并发API调用 (3个线程同时调用)")
print("=" * 70)

results = []
errors = []
lock = threading.Lock()

def call_api(thread_id):
    """并发调用API"""
    try:
        start = time.time()
        resp = requests.post(TEST_URL, headers=headers, json=data, timeout=30)
        elapsed = time.time() - start
        
        with lock:
            if resp.status_code == 200:
                results.append({
                    "thread": thread_id,
                    "time": elapsed,
                    "status": resp.status_code,
                    "success": True
                })
            else:
                errors.append({
                    "thread": thread_id,
                    "time": elapsed,
                    "status": resp.status_code,
                    "error": resp.text[:100]
                })
    except Exception as e:
        with lock:
            errors.append({
                "thread": thread_id,
                "time": 0,
                "error": str(e)[:100]
            })

# 并发执行
start_time = time.time()
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(call_api, i) for i in range(3)]
    for f in as_completed(futures):
        try:
            f.result()
        except Exception as e:
            pass
total_time = time.time() - start_time

print(f"\n并发结果:")
print(f"  成功: {len(results)}")
print(f"  失败: {len(errors)}")
print(f"  总耗时: {total_time:.2f}s")

if results:
    for r in results:
        print(f"  ✓ Thread-{r['thread']}: {r['time']:.2f}s")

if errors:
    for e in errors:
        print(f"  ✗ Thread-{e['thread']}: {e.get('error', e.get('error', 'unknown'))}")

print("\n" + "=" * 70)
