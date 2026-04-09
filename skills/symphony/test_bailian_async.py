import requests
import json

api_key = 'sk-fee678dbf4d84f9a910356821c95c0d5'

# Try creating an async task first
url = 'https://dashscope.aliyuncs.com/api/v1/tasks'

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

data = {
    'model': 'cosyvoice-v2',
    'input': {'text': '你好我是交交'},
    'parameters': {'voice': 'longxiaochun'}
}

resp = requests.post(url, headers=headers, json=data, timeout=8)
print(f'POST /tasks: {resp.status_code} - {resp.text[:200]}')

# Also try GET to list tasks
resp2 = requests.get('https://dashscope.aliyuncs.com/api/v1/tasks', headers=headers, timeout=8)
print(f'GET /tasks: {resp2.status_code} - {resp2.text[:200]}')
