import requests
import os

api_key = os.getenv("NVIDIA_API_KEY", "$NVIDIA_API_KEY")
url = "https://integrate.api.nvidia.com/v1/chat/completions"

# Test Mistral models
models_to_test = [
    ("7", "Mistral Large 2", "mistralai/mistral-large-2-instruct"),
    ("8", "Mistral Small 3.1", "mistralai/mistral-small-3.1-24b-instruct-2503"),
    ("9", "Nemotron 70B", "nvidia/llama-3.1-nemotron-70b-instruct"),
    ("10", "Nemotron Hindi 4B", "nvidia/nemotron-mini-hindi-4b-instruct"),
    ("42", "Mistral Nemo Minitron 8B", "nvidia/mistral-nemo-minitron-8b-8k-instruct"),
]

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

for mid, name, model_id in models_to_test:
    print(f"\n=== Testing {name} ===")
    print(f"Model ID: {model_id}")
    try:
        resp = requests.post(url, headers=headers, json={
            "model": model_id,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 50
        }, timeout=30)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print("✅ OK!")
        else:
            print(f"Error: {resp.text[:200]}")
    except Exception as e:
        print(f"Exception: {e}")
