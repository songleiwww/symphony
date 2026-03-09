# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import requests

print('Checking ModelScope API...')

# 获取可用模型列表
url = 'https://api-inference.modelscope.cn/v1/models'
headers = {
    'Authorization': 'Bearer ms-eac6f154-3502-4721-a168-ce7caeaf1033'
}
try:
    r = requests.get(url, headers=headers, timeout=30)
    print('Status:', r.status_code)
    if r.status_code == 200:
        data = r.json()
        print('Available models:')
        for m in data.get('data', [])[:15]:
            model_id = m.get('id', 'unknown')
            print(' -', model_id)
except Exception as e:
    print('Error:', e)

# 检查火山引擎的embedding
print('\n\nChecking Doubao API...')
url2 = 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions'
headers2 = {
    'Authorization': 'Bearer 3b922877-3fbe-45d1-a298-53f2231c5224',
    'Content-Type': 'application/json'
}
data2 = {
    'model': 'ark-code-latest',
    'messages': [{'role': 'user', 'content': 'Hi'}],
    'max_tokens': 10
}
try:
    r2 = requests.post(url2, headers=headers2, json=data2, timeout=30)
    print('Doubao Status:', r2.status_code)
except Exception as e:
    print('Doubao Error:', e)
