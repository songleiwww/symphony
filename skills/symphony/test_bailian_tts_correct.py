import requests
import json

api_key = 'sk-fee678dbf4d84f9a910356821c95c0d5'

# Try the correct async API format for Bailian
url = 'https://dashscope.aliyuncs.com/api/v1/tasks'

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# Create async task
payload = {
    'model': 'cosyvoice-v2',
    'input': {
        'text': '你好我是交交'
    },
    'parameters': {
        'voice': 'longxiaochun'
    }
}

resp = requests.post(url, headers=headers, json=payload, timeout=10)
print(f'Create task: {resp.status_code}')
print(f'Response: {resp.text[:300]}')

# If task created, get result
if resp.status_code == 200:
    data = resp.json()
    task_id = data.get('task_id')
    print(f'Task ID: {task_id}')
    
    # Get task result
    if task_id:
        get_url = f'https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}'
        resp2 = requests.get(get_url, headers=headers, timeout=10)
        print(f'Get task: {resp2.status_code}')
        print(f'Response: {resp2.text[:500]}')
