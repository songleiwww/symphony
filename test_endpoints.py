#!/usr/bin/env python3
import requests

h = {
    'Authorization': 'Bearer 16cf0a4a775c46cfa1684abcf4b802d0.rtb4oMgpFocBy87y',
    'Content-Type': 'application/json'
}

base = 'https://open.bigmodel.cn/api/paas/v4'

# 测试不同端点
tests = [
    (f'{base}/images/generations', {'model': 'cogview-3-flash', 'prompt': 'test'}),
    (f'{base}/videos/generations', {'model': 'cogvideox-flash', 'prompt': 'test'}),
]

for url, data in tests:
    r = requests.post(url, headers=h, json=data, timeout=30)
    name = url.split('/')[-1]
    print(f'{name}: {r.status_code}')
    print(f'  Response: {r.text[:200]}\n')
