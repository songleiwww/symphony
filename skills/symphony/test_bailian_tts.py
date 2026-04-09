import requests

api_key = 'sk-fee678dbf4d84f9a910356821c95c0d5'

# Try different Bailian TTS endpoints
endpoints = [
    'https://dashscope.aliyuncs.com/api/v1/tts',
    'https://dashscope.aliyuncs.com/api/v1/tts/stream',
    'https://dashscope.aliyuncs.com/api/v1/audio/synthesis',
    'https://dashscope.aliyuncs.com/api/v1/services/audio/tts',
]

headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
data = {'text': 'test', 'model': 'cosyvoice-v2'}

for url in endpoints:
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=8)
        ct = resp.headers.get('Content-Type', 'none')
        print(f'{url}: {resp.status_code} ({ct})')
        if resp.status_code == 200 and 'audio' in ct:
            print('AUDIO FOUND!')
    except Exception as e:
        print(f'{url}: ERROR - {str(e)[:50]}')
