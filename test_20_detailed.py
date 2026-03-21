# -*- coding: utf-8 -*-
"""
序境系统 - 20模型办公测试
"""
import sqlite3
import requests

# Get models from database
conn = sqlite3.connect(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db')
c = conn.cursor()
c.execute('''
    SELECT 模型标识符, 模型名称, 服务商, API地址, API密钥
    FROM 模型配置表
    WHERE 在线状态 = 'online'
    ORDER BY 服务商, id
    LIMIT 20
''')
models = c.fetchall()
conn.close()

# Office test prompt
prompt = '帮我写一封简短的请假邮件，说明身体不适需要休息一天'

results = []
for i, m in enumerate(models, 1):
    identifier, name, provider, api_addr, api_key = m
    status = f'{i}/20 {provider} {name[:25]}'
    print(f'Testing: {status}', end=' ... ')
    try:
        url = api_addr
        headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        data = {
            'model': identifier,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': 200
        }
        resp = requests.post(url, headers=headers, json=data, timeout=20)
        if resp.status_code == 200:
            result = resp.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            preview = content[:80].replace('\n', ' ')
            print(f'OK - {preview}...')
            results.append({'num': i, 'provider': provider, 'name': name, 'status': 'OK', 'preview': preview})
        else:
            print(f'FAIL {resp.status_code}')
            results.append({'num': i, 'provider': provider, 'name': name, 'status': f'FAIL {resp.status_code}'})
    except Exception as e:
        print(f'ERROR')
        results.append({'num': i, 'provider': provider, 'name': name, 'status': 'ERROR'})

print('\n' + '='*60)
print('=== 20模型办公测试结果汇总 ===')
print('='*60)
ok_count = 0
for r in results:
    symbol = '✅' if r['status'] == 'OK' else '❌'
    print(f"{r['num']:2}. {symbol} {r['provider']}: {r['name'][:25]} - {r['status']}")
    if r['status'] == 'OK':
        ok_count += 1

print('='*60)
print(f'总计: {ok_count}/20 成功 ({ok_count*100//20}%)')
print('='*60)
