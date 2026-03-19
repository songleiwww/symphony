import requests
import os

api_key = os.getenv("NVIDIA_API_KEY", "$NVIDIA_API_KEY")
url = "https://integrate.api.nvidia.com/v1/chat/completions"

# Try various Qwen2 model IDs
models_to_test = [
    ("51", "Qwen2 0.5B", "qwen/Qwen2-0.5B-Instruct"),
    ("51", "Qwen2 0.5B", "qwen2-0.5b-instruct"),
    ("52", "Qwen2 1.5B", "qwen/Qwen2-1.5B-Instruct"),
    ("52", "Qwen2 1.5B", "qwen2-1.5b-instruct"),
]

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

for mid, name, model_id in models_to_test:
    print(f"\n=== Testing {name}: {model_id} ===")
    try:
        resp = requests.post(url, headers=headers, json={
            "model": model_id,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 50
        }, timeout=30)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print("✅ OK!")
            break
        else:
            print(f"Error: {resp.text[:150]}")
    except Exception as e:
        print(f"Exception: {e}")
