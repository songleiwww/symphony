import requests
import json

API_KEY = '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'
URL = 'https://integrate.api.nvidia.com/v1/models'
HEADERS = {'Authorization': f'Bearer {API_KEY}'}

r = requests.get(URL, headers=HEADERS, timeout=30)
if r.status_code == 200:
    data = r.json()
    models = data.get('data', [])
    print(f'找到 {len(models)} 个模型')
    print()
    # 查找向量模型
    print('向量/嵌入模型:')
    for m in models:
        name = m.get('id', '')
        if 'embed' in name.lower() or 'retrieval' in name.lower() or 'e5' in name.lower() or 'bge' in name.lower():
            print(f'  - {name}')
    print()
    # 显示所有模型
    print('所有模型:')
    for i, m in enumerate(models):
        print(f'{i+1}. {m.get("id", "unknown")}')
else:
    print(f'错误: {r.status_code}')
