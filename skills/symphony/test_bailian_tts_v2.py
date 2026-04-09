import requests
import json

api_key = 'sk-fee678dbf4d84f9a910356821c95c0d5'

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# Try the service API with correct format
url = 'https://dashscope.aliyuncs.com/api/v1/services/audio/tts'

# Try with full nested task structure
payloads = [
    {
        'model': 'cosyvoice-v2',
        'input': {'text': '你好我是交交'},
        'parameters': {'voice': 'longxiaochun'}
    },
    {
        'model': 'qwen-tts',
        'input': {'text': '你好我是交交'}
    },
    {
        'model': 'sambert-zhinan-v1',
        'input': {'text': '你好我是交交'}
    }
]

for payload in payloads:
    resp = requests.post(url, headers=headers, json=payload, timeout=8)
    print(f'{payload["model"]}: {resp.status_code} - {resp.text[:200]}')
    print()
