# -*- coding: utf-8 -*-
"""
真正并发模型测试 - 使用有效API Key
"""
import requests
import time
import threading
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# 尝试多个API配置
API_CONFIGS = [
    {
        "name": "火山引擎-Code",
        "url": "https://ark.cn-beijing.volces.com/api/coding/v3",
        "key": os.environ.get("ARK_API_KEY", ""),
        "model": "Doubao-Seed-2.0-lite"
    },
    {
        "name": "OpenAI",
        "url": "https://api.openai.com/v1/chat/completions",
        "key": os.environ.get("OPENAI_API_KEY", ""),
        "model": "gpt-4o-mini"
    },
    {
        "name": "硅基流动",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "key": os.environ.get("SILICON_API_KEY", "sk-dummy"),
        "model": "Qwen/Qwen2.5-7B-Instruct"
    }
]

print("=" * 70)
print("真正并发模型API测试")
print("=" * 70)

# 找出可用的API配置
available_config = None
for cfg in API_CONFIGS:
    if cfg["key"]:
        available_config = cfg
        print(f"\n使用API: {cfg['name']}")
        print(f"  URL: {cfg['url'][:50]}...")
        print(f"  Key: {cfg['key'][:20]}...")
        break

if not available_config:
    print("\n没有找到有效的API Key!")
    print("请设置环境变量: ARK_API_KEY 或 OPENAI_API_KEY")
    exit(1)

# 单次调用测试
print("\n[Test 1] 单次API调用...")
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {available_config['key']}"
}

if "openai" in available_config["url"]:
    data = {
        "model": available_config["model"],
        "messages": [{"role": "user", "content": "你好，用一句话介绍自己"}],
        "max_tokens": 100
    }
else:
    data = {
        "model": available_config["model"],
        "messages": [{"role": "user", "content": "你好，用一句话介绍自己"}],
        "max_tokens": 100
    }

try:
    resp = requests.post(available_config["url"], headers=headers, json=data, timeout=30)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        result = resp.json()
        if "choices" in result:
            content = result["choices"][0]["message"]["content"]
            print(f"Response: {content[:200]}")
        else:
            print(f"Response: {result}")
    else:
        print(f"Error: {resp.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# 并发测试
print("\n" + "=" * 70)
print("[Test 2] 并发API调用 (4个线程同时调用)")
print("=" * 70)

results = []
errors = []
lock = threading.Lock()

def call_api(thread_id):
    try:
        start = time.time()
        resp = requests.post(available_config["url"], headers=headers, json=data, timeout=30)
        elapsed = time.time() - start
        
        with lock:
            if resp.status_code == 200:
                result = resp.json()
                content = result["choices"][0]["message"]["content"] if "choices" in result else "N/A"
                results.append({
                    "thread": thread_id,
                    "time": elapsed,
                    "status": resp.status_code,
                    "content": content[:50],
                    "success": True
                })
            else:
                errors.append({
                    "thread": thread_id,
                    "time": elapsed,
                    "status": resp.status_code,
                    "error": resp.text[:50]
                })
    except Exception as e:
        with lock:
            errors.append({
                "thread": thread_id,
                "error": str(e)[:50]
            })

# 并发执行
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
print(f"  平均: {total_time/4:.2f}s/请求")

if results:
    print("\n成功案例:")
    for r in results:
        print(f"  [OK] Thread-{r['thread']}: {r['time']:.2f}s - {r['content']}")

if errors:
    print("\n失败案例:")
    for e in errors:
        print(f"  [FAIL] Thread-{e['thread']}: {e.get('error', 'unknown')}")

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)
