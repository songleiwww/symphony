# -*- coding: utf-8 -*-
import requests

keys = [
    ("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", "nvidia/llama-3.1-nemotron-70b-instruct"),
    ("ms-eac6f154-3502-4721-a168-ce75d7e0e4b11", "microsoft/Phi-3-mini-128k-instruct"),
]

print("=== 测试两个密钥 ===\n")

for key, model in keys:
    print(f"Key: {key[:25]}...")
    print(f"Model: {model}")
    
    if key.startswith("nvapi"):
        url = "https://integrate.api.nvidia.com/v1/chat/completions"
    else:
        url = "https://models.inference.ai.azure.com/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text[:80]}")
    except Exception as e:
        print(f"Exception: {str(e)[:40]}")
    print()
