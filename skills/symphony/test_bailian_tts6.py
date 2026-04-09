import requests
import json

api_key = 'sk-fee678dbf4d84f9a910356821c95c0d5'

# Get model list
url = 'https://dashscope.aliyuncs.com/api/v1/models'
headers = {'Authorization': f'Bearer {api_key}'}

resp = requests.get(url, headers=headers, timeout=8)
print('Status:', resp.status_code)
data = resp.json()
print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
