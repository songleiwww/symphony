# -*- coding: utf-8 -*-
import sqlite3
import requests

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
c = conn.cursor()

# 先查看表结构
c.execute("PRAGMA table_info(模型配置表)")
cols = c.fetchall()
print("表结构:", [col[1] for col in cols])

# 获取所有启用的模型
c.execute('SELECT * FROM 模型配置表')
rows = c.fetchall()

print(f'\n=== 模型配置表在线状态检测 ===\n')
print(f'ID | 模型名称 | 服务商 | 状态')
print('-' * 50)

results = []
for row in rows:
    model_id = row[0]
    model_name = row[1]
    model_id_raw = row[2]
    provider = row[3]
    api_url = row[4]
    api_key = row[5]
    enabled = row[6]
    
    if enabled != '启用':
        continue
    
    # 测试API连通性
    online = '⏳'
    try:
        headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        data = {'model': model_id_raw, 'messages': [{'role': 'user', 'content': 'hi'}], 'max_tokens': 5}
        resp = requests.post(f'{api_url}/chat/completions', headers=headers, json=data, timeout=10)
        online = '✅' if resp.status_code == 200 else f'❌{resp.status_code}'
    except Exception as e:
        online = '❌'
    
    print(f'{model_id} | {model_name[:20]} | {provider[:6]} | {online}')
    results.append({'id': model_id, 'name': model_name, 'provider': provider, 'status': online})

print(f'\n总计: {len(results)} 个模型')
online_count = sum(1 for r in results if '✅' in r['status'])
print(f'在线: {online_count} | 离线: {len(results) - online_count}')

conn.close()
