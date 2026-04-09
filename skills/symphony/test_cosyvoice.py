import requests
import json

api_key = 'sk-fee678dbf4d84f9a910356821c95c0d5'

# Correct Bailian TTS API format
url = 'https://dashscope.aliyuncs.com/api/v1/services/audio/tts'

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# CosyVoice-v2 format
data = {
    'model': 'cosyvoice-v2',
    'input': {
        'text': '你好，我是交交。'
    },
    'parameters': {
        'voice': 'longxiaochun'
    }
}

resp = requests.post(url, headers=headers, json=data, timeout=10)
print('Status:', resp.status_code)
print('Response:', resp.text[:500] if resp.text else 'empty')
