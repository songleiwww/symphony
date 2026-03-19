# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

print('=== Dispatch History ===\n')

# Get model usage stats
cur.execute('SELECT model_name, COUNT(*) as cnt FROM "调度历史表" GROUP BY model_name ORDER BY cnt DESC')
print('Model usage:')
for r in cur.fetchall():
    print(f'  {r[0]}: {r[1]} times')

# Get role usage stats
cur.execute('SELECT role_id, COUNT(*) as cnt FROM "调度历史表" GROUP BY role_id ORDER BY cnt DESC')
print('\nRole usage:')
for r in cur.fetchall():
    print(f'  {r[0]}: {r[1]} times')

# Get model config for provider info
print('\n=== Model Config (Provider Info) ===')
cur.execute('SELECT "模型名称", "服务商" FROM "模型配置表" WHERE "模型名称" IN (SELECT DISTINCT model_name FROM "调度历史表")')
for r in cur.fetchall():
    print(f'  {r[0]}: {r[1]}')

conn.close()
