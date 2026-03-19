import requests
import os

api_key = os.getenv("NVIDIA_API_KEY", "$NVIDIA_API_KEY")
url = "https://integrate.api.nvidia.com/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

print("=== 测试 nvidia/llama-3.1-nemoguard-8b-content-safety ===")

try:
    resp = requests.post(url, headers=headers, json={
        "model": "nvidia/llama-3.1-nemoguard-8b-content-safety",
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 50
    }, timeout=30)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print("✅ 可用!")
    else:
        print(f"Error: {resp.text[:200]}")
except Exception as e:
    print(f"Exception: {e}")
