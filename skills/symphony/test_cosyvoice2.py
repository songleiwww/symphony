import requests
import json

api_key = 'sk-fee678dbf4d84f9a910356821c95c0d5'

url = 'https://dashscope.aliyuncs.com/api/v1/services/audio/tts'

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# Try with task wrapper
payloads = [
    {'model': 'cosyvoice-v2', 'input': {'text': '你好我是交交'}, 'parameters': {'voice': 'longxiaochun'}},
    {'model': 'cosyvoice-v2', 'task': {'input': {'text': '你好我是交交'}}, 'parameters': {'voice': 'longxiaochun'}},
    {'task': {'model': 'cosyvoice-v2', 'input': {'text': '你好我是交交'}, 'parameters': {'voice': 'longxiaochun'}}},
    {'model': 'cosyvoice-v2', 'text': '你好我是交交', 'voice': 'longxiaochun'},
]

for data in payloads:
    resp = requests.post(url, headers=headers, json=data, timeout=8)
    print(f'Payload: {json.dumps(data, ensure_ascii=False)[:80]}')
    print(f'Status: {resp.status_code}, Response: {resp.text[:150]}')
    print()
