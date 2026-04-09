import requests
import json

api_key = 'sk-fee678dbf4d84f9a910356821c95c0d5'

all_models = []
page_no = 1
page_size = 50

while True:
    url = f'https://dashscope.aliyuncs.com/api/v1/models?page_no={page_no}&page_size={page_size}'
    headers = {'Authorization': f'Bearer {api_key}'}
    
    resp = requests.get(url, headers=headers, timeout=15)
    data = resp.json()
    
    models = data.get('output', {}).get('models', [])
    all_models.extend(models)
    
    total = data.get('output', {}).get('total', 0)
    print(f'Page {page_no}: got {len(models)} models, total so far: {len(all_models)}/{total}')
    
    if len(all_models) >= total:
        break
    page_no += 1

print(f'\nTotal models retrieved: {len(all_models)}')

# Filter for speech/audio related
speech_kw = ['tts', 'asr', 'audio', 'speech', 'cosy', 'voice', 'paraphrase', 'sambert', 'paraformer']
speech_models = [m for m in all_models if any(k in m.get('model', '').lower() for k in speech_kw)]
print(f'Speech/Audio models: {len(speech_models)}')
for m in speech_models:
    print(f'  - {m["model"]}')

# List all unique prefixes
prefixes = set()
for m in all_models:
    name = m.get('model', '')
    if '.' in name:
        prefixes.add(name.split('.')[0])
print(f'\nAll prefixes: {sorted(prefixes)}')
