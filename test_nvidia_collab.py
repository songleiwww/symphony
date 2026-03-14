# -*- coding: utf-8 -*-
"""
NVIDIA 并发模型测试 - 使用可用的Mixtral模型
"""
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

print("=" * 70)
print("NVIDIA 并发模型测试")
print("=" * 70)

TEST_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
TEST_KEY = "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"
TEST_MODEL = "mistralai/mixtral-8x7b-instruct-v0.1"

print(f"模型: {TEST_MODEL}")

headers = {"Content-Type": "application/json", "Authorization": f"Bearer {TEST_KEY}"}
data = {"model": TEST_MODEL, "messages": [{"role": "user", "content": "用一句话介绍自己"}], "max_tokens": 50}

# Test 1: 单次调用
print("\n[Test 1] 单次调用...")
resp = requests.post(TEST_URL, headers=headers, json=data, timeout=60)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    print(f"Response: {resp.json()['choices'][0]['message']['content'][:100]}")

# Test 2: 并发4次
print("\n[Test 2] 并发4次调用...")
results, errors, lock = [], [], threading.Lock()

def call(i):
    t = time.time()
    r = requests.post(TEST_URL, headers=headers, json=data, timeout=60)
    with lock:
        if r.status_code == 200:
            results.append({"i": i, "t": time.time()-t, "r": r.json()["choices"][0]["message"]["content"][:30]})
        else:
            errors.append({"i": i, "e": r.text[:50]})

st = time.time()
with ThreadPoolExecutor(max_workers=4) as e:
    list(e.map(call, range(4)))
print(f"总耗时: {time.time()-st:.2f}s")
print(f"成功: {len(results)}, 失败: {len(errors)}")
for r in results: print(f"  [OK] Thread-{r['i']}: {r['t']:.2f}s - {r['r']}")
for e in errors: print(f"  [FAIL] Thread-{e['i']}: {e['e']}")

print("\n" + "=" * 70)
