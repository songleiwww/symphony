#!/usr/bin/env python3
import requests

base = 'https://open.bigmodel.cn/api/paas/v4'
h = {
    'Authorization': 'Bearer 16cf0a4a775c46cfa1684abcf4b802d0.rtb4oMgpFocBy87y',
    'Content-Type': 'application/json'
}

# 获取模型列表
print('=== 模型列表 ===')
r = requests.get(f'{base}/models', headers=h, timeout=30)
print(f'Status: {r.status_code}')
if r.status_code == 200:
    import json
    data = r.json()
    for m in data.get('data', []):
        print(f"  - {m.get('id')}")

print('\n=== 图像生成 ===')
img_data = {'model': 'cogview-3-flash', 'prompt': '一只蓝色小猫'}
r = requests.post(f'{base}/images/generations', headers=h, json=img_data, timeout=60)
print(f'Status: {r.status_code}')
print(f'Response: {r.text[:500]}')

print('\n=== 视频生成 ===')
vid_data = {'model': 'cogvideox-flash', 'prompt': '一只小猫'}
r = requests.post(f'{base}/videos/generations', headers=h, json=vid_data, timeout=60)
print(f'Status: {r.status_code}')
print(f'Response: {r.text[:500]}')
