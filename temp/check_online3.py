# -*- coding: utf-8 -*-
import sqlite3
import requests

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
c = conn.cursor()

# 获取所有数据
c.execute('SELECT * FROM 模型配置表')
rows = c.fetchall()

# 列名
columns = ['id', '模型名称', '模型标识', '模型类型', '服务商', 'API地址', 'API密钥', '是否启用', '使用场景', '创建时间', '更新时间']

print('=== 模型配置表在线状态检测 ===\n')
print(f'ID  模型名称                    服务商     状态')
print('-' * 70)

results = []
for row in rows:
    model_id = row[0]
    model_name = row[1]
    model_id_raw = row[2]
    model_type = row[3]
    provider = row[4]
    api_url = row[5]
    api_key = row[6]
    enabled = row[7]
    
    if enabled != '启用':
        continue
    
    # 测试API连通性
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
    
    print(f'{model_id:<3} {model_name:<24} {provider:<9} {online}')
    results.append({'id': model_id, 'name': model_name, 'provider': provider, 'status': online})

print(f'\n总计: {len(results)} 个启用模型')
online_count = sum(1 for r in results if '✅' in r['status'])
print(f'在线: {online_count} | 离线: {len(results) - online_count}')

conn.close()
