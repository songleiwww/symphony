import requests
import json

api_key = 'sk-fee678dbf4d84f9a910356821c95c0d5'

url = 'https://dashscope.aliyuncs.com/api/v1/services/audio/tts'

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# Try with empty task object
tests = [
    {'model': 'cosyvoice-v2', 'task': {}, 'input': {'text': '你好我是交交'}},
    {'model': 'cosyvoice-v2', 'task': {'input': {'text': '你好我是交交'}}, 'input': {'text': '你好我是交交'}},
    {'model': 'cosyvoice-v2', 'task': '', 'input': {'text': '你好我是交交'}},
    {'task': {'model': 'cosyvoice-v2', 'input': {'text': '你好我是交交', 'voice': 'longxiaochun'}}},
    {'model': 'cosyvoice-v2', 'input': {'text': '你好我是交交'}, 'task': {'input': {'text': '你好我是交交'}}},
]

for data in tests:
    resp = requests.post(url, headers=headers, json=data, timeout=8)
    print(f'Status: {resp.status_code}, Resp: {resp.text[:120]}')
