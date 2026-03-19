# -*- coding: utf-8 -*-
import requests

API_KEY = "nvapi-6P3DqO8lEWy1qqUweaM2bmLr"

# Try different endpoints
endpoints = [
    "https://integrate.api.nvidia.com/v1/chat/completions",
    "https://integrate.api.nvidia.com/v1/models",
    "https://api.nvidia.com/v1/chat/completions",
]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "jamba-1.5-mini",
    "messages": [{"role": "user", "content": "hi"}],
    "max_tokens": 30
}

print("=== Testing NVIDIA Endpoints ===\n")

for url in endpoints:
    print(f"Testing: {url}")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  SUCCESS!")
            break
    except Exception as e:
        print(f"  Error: {str(e)[:50]}")
    print()
