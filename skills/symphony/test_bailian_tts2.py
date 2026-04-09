import requests
import json

api_key = 'sk-fee678dbf4d84f9a910356821c95c0d5'

# Correct Bailian TTS API format
url = 'https://dashscope.aliyuncs.com/api/v1/services/audio/tts'

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# Try different payload formats
payloads = [
    {'text': '你好', 'model': 'cosyvoice-v2'},
    {'text': '你好', 'model': 'cosyvoice-v2', 'voice': 'longxiaochun'},
    {'text': '你好', 'model': 'cosyvoice-v2', 'format': 'mp3'},
    {'text': '你好我是交交', 'model': 'cosyvoice', 'voice': 'longxiaochun', 'sample_rate': 24000},
]

for data in payloads:
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=8)
        ct = resp.headers.get('Content-Type', '')
        print(f'{data}: {resp.status_code} ({ct[:30]})')
        if resp.status_code == 200:
            print('SUCCESS!')
            print('Content length:', len(resp.content))
    except Exception as e:
        print(f'{data}: ERROR - {str(e)[:50]}')
