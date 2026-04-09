import requests
import json

api_key = 'sk-fee678dbf4d84f9a910356821c95c0d5'

# Try async task creation approach
url = 'https://dashscope.aliyuncs.com/api/v1/audio/tts'

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

data = {
    'model': 'cosyvoice-v2',
    'text': '你好我是交交',
    'voice': 'longxiaochun'
}

resp = requests.post(url, headers=headers, json=data, timeout=8)
print(f'/audio/tts: {resp.status_code} - {resp.text[:200]}')

# Try synthesis
url2 = 'https://dashscope.aliyuncs.com/api/v1/audio/synthesis'
resp2 = requests.post(url2, headers=headers, json=data, timeout=8)
print(f'/audio/synthesis: {resp2.status_code} - {resp2.text[:200]}')

# Try with correct async format
url3 = 'https://dashscope.aliyuncs.com/api/v1/services/audio/tts/async'
data3 = {
    'model': 'cosyvoice-v2',
    'input': {'text': '你好我是交交'},
    'parameters': {'voice': 'longxiaochun'}
}
resp3 = requests.post(url3, headers=headers, json=data3, timeout=8)
print(f'/async: {resp3.status_code} - {resp3.text[:300]}')
