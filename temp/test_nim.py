# -*- coding: utf-8 -*-
import requests

API_KEY = "nvapi-6P3DqO8lEWy1qqUweaM2bmLr"

# Test NVIDIA NIM API
# Based on NVIDIA official documentation
endpoints = [
    # NIM API endpoints
    "https://integrate.api.nvidia.com/v1/models/meshhq/meshchat/chat/completions",
    "https://nvbugsprod鸠田.azure-api.net/v1/chat/completions",
]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Try with different model names that are known to work
test_configs = [
    {"model": "nvidia/llama-3.1-nemotron-70b-instruct", "url": "https://integrate.api.nvidia.com/v1/chat/completions"},
    {"model": "nvidia/llama-3.1-405b-instruct", "url": "https://integrate.api.nvidia.com/v1/chat/completions"},
    {"model": "mistralai/mixtral-8x7b-instruct-v0.1", "url": "https://integrate.api.nvidia.com/v1/chat/completions"},
    {"model": "google/gemma-2-2b-it", "url": "https://integrate.api.nvidia.com/v1/chat/completions"},
    {"model": "google/gemma-2-9b-it", "url": "https://integrate.api.nvidia.com/v1/chat/completions"},
]

print("=== Testing NVIDIA NIM Models ===\n")

for cfg in test_configs:
    print(f"Testing: {cfg['model']}")
    
    payload = {
        "model": cfg["model"],
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 30
    }
    
    try:
        response = requests.post(cfg["url"], headers=headers, json=payload, timeout=20)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  SUCCESS!")
            break
        else:
            print(f"  Error: {response.text[:80]}")
    except Exception as e:
        print(f"  Error: {str(e)[:50]}")
    print()
