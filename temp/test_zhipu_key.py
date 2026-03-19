# -*- coding: utf-8 -*-
import requests

# 使用数据库中的正确密钥测试
api_key = "83e29cfa875a48d99064a8d0c6977a7f.XuH7V1qGZoOZ1lO6"

print("=== 使用数据库密钥测试智谱 ===\n")

endpoints = [
    ("https://open.bigmodel.cn/api/paas/v4/chat/completions", "glm-4-flash"),
    ("https://open.bigmodel.cn/api/paas/v4/chat/completions", "glm-4"),
]

for url, model in endpoints:
    print(f"Testing: {model}")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 20
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  SUCCESS!")
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"  Response: {content[:50]}")
            break
        else:
            print(f"  Error: {response.text[:80]}")
    except Exception as e:
        print(f"  Error: {str(e)[:50]}")
    print()
