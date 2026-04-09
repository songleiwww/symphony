import requests
import json

api_key = 'sk-fee678dbf4d84f9a910356821c95c0d5'

url = 'https://dashscope.aliyuncs.com/api/v1/services/audio/tts'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}
data = {'text': '你好我是交交', 'model': 'cosyvoice-v2'}

resp = requests.post(url, headers=headers, json=data, timeout=8)
print('Status:', resp.status_code)
print('Response:', resp.text)
