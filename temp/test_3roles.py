import requests

# 使用数据库中配置的官署角色模型
# 角色1: 陆念昭 -> 火山引擎 ark-code-latest
# 角色2: 徐浩 -> 火山引擎 deepseek-v3.2  
# 角色3: 郭熙 -> 英伟达 Nemoguard 8B

print('='*60)
print('序境调度 - 模型组合技能测试')
print('='*60)

# 测试角色1: 陆念昭
print('\n【角色1: 陆念昭(少府监)】')
print('模型: ark-code-latest (火山引擎)')
url1 = 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions'
headers1 = {'Authorization': 'Bearer 3b922877-3fbe-45d1-a298-53f2230f0d92', 'Content-Type': 'application/json'}
data1 = {'model': 'doubao-seed-2.0-pro', 'messages': [{'role': 'user', 'content': '你好'}], 'max_tokens': 50}
try:
    r1 = requests.post(url1, headers=headers1, json=data1, timeout=20)
    print(f'状态: {r1.status_code}')
    if r1.status_code == 200:
        print(f'响应: {r1.json()[\"choices\"][0][\"message\"][\"content\"][:80]}')
except Exception as e:
    print(f'异常: {e}')

# 测试角色2: 徐浩
print('\n【角色2: 徐浩(中尚令)】')
print('模型: deepseek-v3.2 (火山引擎)')
data2 = {'model': 'deepseek-v3-2-250121', 'messages': [{'role': 'user', 'content': '你好'}], 'max_tokens': 50}
try:
    r2 = requests.post(url1, headers=headers1, json=data2, timeout=20)
    print(f'状态: {r2.status_code}')
    if r2.status_code == 200:
        print(f'响应: {r2.json()[\"choices\"][0][\"message\"][\"content\"][:80]}')
except Exception as e:
    print(f'异常: {e}')

# 测试角色3: 郭熙
print('\n【角色3: 郭熙(左尚令)】')
print('模型: Nemoguard 8B (英伟达)')
url3 = 'https://integrate.api.nvidia.com/v1/chat/completions'
headers3 = {'Authorization': 'Bearer nvapi-6P3DqO8lEWy1qqUweaM2bmLr', 'Content-Type': 'application/json'}
data3 = {'model': 'nvidia/nemoguard-8b', 'messages': [{'role': 'user', 'content': '你好'}], 'max_tokens': 50}
try:
    r3 = requests.post(url3, headers=headers3, json=data3, timeout=20)
    print(f'状态: {r3.status_code}')
    if r3.status_code == 200:
        print(f'响应: {r3.json()[\"choices\"][0][\"message\"][\"content\"][:80]}')
except Exception as e:
    print(f'异常: {e}')

print('\n' + '='*60)
print('测试完成')
print('='*60)
