import sqlite3
import requests
c = sqlite3.connect('C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db')
c.text_factory = str

# Find the model config table
tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
model_table = None
for t in tables:
    if '模型' in t and '配置' in t:
        model_table = t
        break

print('=== 模型配置表在线状态检测 ===\n')

# Get all data
rows = c.execute(f"SELECT * FROM '{model_table}'").fetchall()

# Column indices (0-based)
IDX_ID = 0
IDX_NAME = 1
IDX_MODEL_ID = 2
IDX_TYPE = 3
IDX_PROVIDER = 4
IDX_API_URL = 5
IDX_API_KEY = 6
IDX_STATUS = 7

print(f"{'ID':<4} {'模型名称':<28} {'服务商':<10} {'状态'}")
print('-' * 70)

results = []
for row in rows:
    # Check if model is enabled (status = '正常')
    if row[IDX_STATUS] != '正常':
        continue
    
    model_id = row[IDX_ID]
    model_name = row[IDX_NAME]
    model_id_raw = row[IDX_MODEL_ID]
    provider = row[IDX_PROVIDER]
    api_url = row[IDX_API_URL]
    api_key = row[IDX_API_KEY]
    
    # Test API
    online = '⏳'
    try:
        headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        data = {'model': model_id_raw, 'messages': [{'role': 'user', 'content': 'hi'}], 'max_tokens': 5}
        resp = requests.post(f'{api_url}/chat/completions', headers=headers, json=data, timeout=10)
        if resp.status_code == 200:
            online = '✅在线'
        else:
            online = f'❌{resp.status_code}'
    except Exception as e:
        online = '❌超时'
    
    print(f'{model_id:<4} {model_name[:26]:<28} {provider[:8]:<10} {online}')
    results.append({'id': model_id, 'name': model_name, 'provider': provider, 'status': online})

print(f'\n总计: {len(results)} 个启用模型')
online_count = sum(1 for r in results if '✅' in r['status'])
print(f'在线: {online_count} | 离线: {len(results) - online_count}')

c.close()
