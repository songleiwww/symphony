# -*- coding: utf-8 -*-
import requests

NEW_KEY = "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"

# Get models list
url = "https://integrate.api.nvidia.com/v1/models"
headers = {"Authorization": f"Bearer {NEW_KEY}"}
r = requests.get(url, timeout=10)
models = [m["id"] for m in r.json().get("data", [])] if r.status_code == 200 else []
print(f"Models: {len(models)}")

# Test user's model
url = "https://integrate.api.nvidia.com/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {NEW_KEY}",
    "Accept": "application/json"
}

payload = {
    "model": "qwen/qwen3.5-122b-a10b",
    "messages": [{"role":"user","content":"hi"}],
    "max_tokens": 10,
}

print("Testing qwen/qwen3.5-122b-a10b...")
resp = requests.post(url, headers=headers, json=payload, timeout=15)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    print("SUCCESS!")
    print(resp.json())
else:
    print(f"Error: {resp.text[:200]}")
