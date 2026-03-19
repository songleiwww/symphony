import requests
import json

# 模型1: 火山引擎 ark-code-latest
url1 = 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions'
headers1 = {
    'Authorization': 'Bearer 3b922877-3fbe-45d1-a298-53f2230f0d92',
    'Content-Type': 'application/json'
}
data1 = {
    'model': 'doubao-seed-2.0-pro',
    'messages': [{'role': 'user', 'content': '你好，用一句话介绍自己'}],
    'max_tokens': 100
}

print('=== 调用模型1: 火山引擎 ===')
try:
    r1 = requests.post(url1, headers=headers1, json=data1, timeout=30)
    print(f'状态: {r1.status_code}')
    if r1.status_code == 200:
        result = r1.json()
        content = result["choices"][0]["message"]["content"]
        print(f'响应: {content[:100]}...')
    else:
        print(f'错误: {r1.text[:200]}')
except Exception as e:
    print(f'异常: {e}')

print()

# 模型2: 智谱 GLM-4 Flash
url2 = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
headers2 = {
    'Authorization': 'Bearer a2afbc521cb24dfca766928d9fbb119c',
    'Content-Type': 'application/json'
}
data2 = {
    'model': 'glm-4-flash',
    'messages': [{'role': 'user', 'content': '你好，用一句话介绍自己'}],
    'max_tokens': 100
}

print('=== 调用模型2: 智谱GLM-4 Flash ===')
try:
    r2 = requests.post(url2, headers=headers2, json=data2, timeout=30)
    print(f'状态: {r2.status_code}')
    if r2.status_code == 200:
        result = r2.json()
        content = result["choices"][0]["message"]["content"]
        print(f'响应: {content[:100]}...')
    else:
        print(f'错误: {r2.text[:200]}')
except Exception as e:
    print(f'异常: {e}')
