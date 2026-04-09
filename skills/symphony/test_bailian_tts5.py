import requests
import json

api_key = 'sk-fee678dbf4d84f9a910356821c95c0d5'

# Try to get model list
url = 'https://dashscope.aliyuncs.com/api/v1/models'
headers = {'Authorization': f'Bearer {api_key}'}

try:
    resp = requests.get(url, headers=headers, timeout=8)
    print('Status:', resp.status_code)
    data = resp.json()
    # Filter for audio/tts models
    if 'data' in data:
        for model in data['data']:
            if 'tts' in model.get('id', '').lower() or 'audio' in model.get('id', '').lower() or 'cosy' in model.get('id', '').lower():
                print('TTS Model:', model)
except Exception as e:
    print('Error:', e)

# Also try listing available models
url2 = 'https://dashscope.aliyuncs.com/api/v1/services'
headers2 = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}
try:
    resp2 = requests.get(url2, headers=headers2, timeout=8)
    print('Services Status:', resp2.status_code)
    print('Services Response:', resp2.text[:500])
except Exception as e:
    print('Services Error:', e)
