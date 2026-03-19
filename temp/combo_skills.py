import requests

print('='*60)
print('官署角色组合技能 - 真实API调用')
print('='*60)

# 1. 陆念昭 - 火山引擎 ark-code-latest
print('\n【1】陆念昭(少府监) - ark-code-latest')
url = 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions'
h = {'Authorization': 'Bearer 3b922877-3fbe-45d1-a298-53f2231c5224', 'Content-Type': 'application/json'}
d = {'model': 'doubao-seed-2.0-pro', 'messages': [{'role': 'user', 'content': '用一句话介绍你的官职'}], 'max_tokens': 50}
r = requests.post(url, headers=h, json=d, timeout=15)
print(f'状态: {r.status_code}')
if r.status_code == 200:
    c = r.json()['choices'][0]['message']['content']
    print(f'响应: {c[:80]}')

# 2. 徐浩 - 火山引擎 deepseek-v3.2
print('\n【2】徐浩(中尚令) - deepseek-v3.2')
d2 = {'model': 'deepseek-v3-2-250121', 'messages': [{'role': 'user', 'content': '用一句话介绍你的官职'}], 'max_tokens': 50}
r2 = requests.post(url, headers=h, json=d2, timeout=15)
print(f'状态: {r2.status_code}')
if r2.status_code == 200:
    c2 = r2.json()['choices'][0]['message']['content']
    print(f'响应: {c2[:80]}')

# 3. 郭熙 - 英伟达
print('\n【3】郭熙(左尚令) - 英伟达')
url3 = 'https://integrate.api.nvidia.com/v1/chat/completions'
h3 = {'Authorization': 'Bearer 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', 'Content-Type': 'application/json'}
d3 = {'model': 'nvidia/nemoguard-8b', 'messages': [{'role': 'user', 'content': '用一句话介绍你的官职'}], 'max_tokens': 50}
r3 = requests.post(url3, headers=h3, json=d3, timeout=15)
print(f'状态: {r3.status_code}')
if r3.status_code == 200:
    c3 = r3.json()['choices'][0]['message']['content']
    print(f'响应: {c3[:80]}')
else:
    print(f'错误: {r3.text[:100]}')

print('\n组合技能测试完成')
