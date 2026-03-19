# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Check what providers exist
cur.execute('SELECT DISTINCT 服务商 FROM 模型配置表')
rows = cur.fetchall()

print('=== All Providers in DB ===')
for r in rows:
    print(f"Provider: {r[0]}")

# Count by provider
cur.execute('SELECT 服务商, COUNT(*) FROM 模型配置表 WHERE 在线状态="online" GROUP BY 服务商')
rows = cur.fetchall()

print('\n=== Online Models by Provider ===')
for r in rows:
    print(f"Provider: {r[0]}, Count: {r[1]}")

# Check models with modelscope URL
cur.execute('SELECT id, 模型名称, 服务商, API地址 FROM 模型配置表 WHERE API地址 LIKE "%modelscope%"')
rows = cur.fetchall()

print('\n=== Models with ModelScope URL ===')
for r in rows:
    print(f"ID:{r[0]} Name:{r[1]} Provider:{r[2]} URL:{r[3]}")

conn.close()
