import requests
import json

api_key = 'sk-fee678dbf4d84f9a910356821c95c0d5'

# Try Sambert TTS which might have different API
tests = [
    # Sambert format
    ('https://dashscope.aliyuncs.com/api/v1/services/audio/tts', {
        'model': 'sambert-zhinan-v1',
        'input': {'text': '你好我是交交'}
    }),
    # Try with voice in input
    ('https://dashscope.aliyuncs.com/api/v1/services/audio/tts', {
        'model': 'cosyvoice-v2',
        'input': {'text': '你好我是交交', 'voice': 'longxiaochun'}
    }),
    # Try qwen-tts-latest
    ('https://dashscope.aliyuncs.com/api/v1/services/audio/tts', {
        'model': 'qwen-tts-latest',
        'input': {'text': '你好我是交交'}
    }),
]

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

for url, data in tests:
    resp = requests.post(url, headers=headers, json=data, timeout=8)
    print(f'{data["model"]}: {resp.status_code} - {resp.text[:150]}')
