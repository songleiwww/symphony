import requests
import json

api_key = 'sk-fee678dbf4d84f9a910356821c95c0d5'

url = 'https://dashscope.aliyuncs.com/api/v1/models'
headers = {'Authorization': f'Bearer {api_key}'}

resp = requests.get(url, headers=headers, timeout=15)
data = resp.json()

# Search for TTS or audio models
models = data.get('output', {}).get('models', [])
tts_models = [m for m in models if any(k in m.get('model', '').lower() for k in ['tts', 'audio', 'cosy', 'speech'])]
print(f'Found {len(tts_models)} TTS/audio models:')
for m in tts_models[:20]:
    print(f'  - {m["model"]}')
