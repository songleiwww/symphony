#!/usr/bin/env python3
import requests
import time

base = 'https://open.bigmodel.cn/api/paas/v4'
h = {
    'Authorization': 'Bearer 16cf0a4a775c46cfa1684abcf4b802d0.rtb4oMgpFocBy87y',
    'Content-Type': 'application/json'
}

print('=== 通过Chat Completions调用 ===')

# 1. 先测试普通文本模型确认API正常
print('\n1. 测试GLM-4-Flash:')
data = {'model': 'glm-4-flash', 'messages': [{'role':'user','content':'hi'}], 'max_tokens': 50}
r = requests.post(f'{base}/chat/completions', headers=h, json=data, timeout=30)
print(f'  Status: {r.status_code}')

# 等待一下
time.sleep(1)

# 2. 测试CogView图像生成
print('\n2. 测试CogView-3-Flash图像生成:')
data = {'model': 'cogview-3-flash', 'messages': [{'role':'user','content':'生成一只蓝色小猫图片'}], 'max_tokens': 1000}
r = requests.post(f'{base}/chat/completions', headers=h, json=data, timeout=60)
print(f'  Status: {r.status_code}')
if r.status_code == 200:
    result = r.json()
    content = result['choices'][0]['message']['content']
    print(f'  Content type: {type(content)}')
    if isinstance(content, list):
        for item in content:
            if item.get('type') == 'image_url':
                print(f'  Image URL: {item.get("image_url",{}).get("url","")[:100]}')
    else:
        print(f'  Content: {str(content)[:200]}')
else:
    print(f'  Error: {r.text[:200]}')

# 等待一下
time.sleep(1)

# 3. 测试CogVideoX
print('\n3. 测试CogVideoX-Flash视频生成:')
data = {'model': 'cogvideox-flash', 'messages': [{'role':'user','content':'生成一个可爱小猫的视频'}], 'max_tokens': 2000}
r = requests.post(f'{base}/chat/completions', headers=h, json=data, timeout=60)
print(f'  Status: {r.status_code}')
print(f'  Response: {r.text[:500]}')
