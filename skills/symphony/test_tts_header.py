import requests
import json

api_key = 'sk-fee678dbf4d84f9a910356821c95c0d5'

# Try with X-DashScope-Model header
url = 'https://dashscope.aliyuncs.com/api/v1/services/audio/tts'

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
    'X-DashScope-Model': 'cosyvoice-v2'
}

data = {
    'input': {'text': '你好我是交交'},
    'parameters': {'voice': 'longxiaochun'}
}

resp = requests.post(url, headers=headers, json=data, timeout=8)
print(f'Status: {resp.status_code}')
print(f'Response: {resp.text[:300]}')

# Try with task in different format
print('\n--- Trying different format ---')
data2 = {
    'task': {
        'input': {'text': '你好我是交交'}
    }
}
resp2 = requests.post(url, headers=headers, json=data2, timeout=8)
print(f'Status: {resp2.status_code}')
print(f'Response: {resp2.text[:300]}')
