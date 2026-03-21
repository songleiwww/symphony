# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 检查各服务商API配置
providers = ['英伟达', '硅基流动', '魔搭']
for p in providers:
    c.execute("SELECT 模型名称, API地址, API密钥, 在线状态 FROM 模型配置表 WHERE 服务商=? LIMIT 2", (p,))
    print(f'\n【{p}】')
    for row in c.fetchall():
        print(f'  模型: {row[0]}')
        print(f'  API: {row[1]}')
        print(f'  Key: {row[2][:30] if row[2] else "None"}...')
        print(f'  状态: {row[3]}')

conn.close()
