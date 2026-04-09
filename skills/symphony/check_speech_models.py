import requests
import json

api_key = 'sk-fee678dbf4d84f9a910356821c95c0d5'

url = 'https://dashscope.aliyuncs.com/api/v1/models'
headers = {'Authorization': f'Bearer {api_key}'}

resp = requests.get(url, headers=headers, timeout=15)
data = resp.json()

models = data.get('output', {}).get('models', [])
print(f'Total models: {len(models)}')

# Filter for speech/audio related
speech_kw = ['tts', 'asr', 'audio', 'speech', 'cosy', 'voice', 'paraphrase', 'sambert']
speech_models = [m for m in models if any(k in m.get('model', '').lower() for k in speech_kw)]
print(f'Speech/Audio models: {len(speech_models)}')
for m in speech_models:
    print(f'  - {m["model"]}')

# Also print all unique model name prefixes
prefixes = set()
for m in models:
    name = m.get('model', '')
    if '.' in name:
        prefixes.add(name.split('.')[0])
print(f'\nModel prefixes: {sorted(prefixes)}')
