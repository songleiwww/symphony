# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Check binding status
cur.execute('SELECT COUNT(*) FROM "官署角色表" WHERE 模型配置表_ID IS NOT NULL')
bound = cur.fetchone()[0]

cur.execute('SELECT COUNT(*) FROM "官署角色表" WHERE 模型配置表_ID IS NULL')
unbound = cur.fetchone()[0]

print('=== Binding Status ===')
print(f'已绑定模型: {bound}')
print(f'未绑定模型: {unbound}')
print(f'总计: {bound + unbound}')

# Check a sample bound record
cur.execute('SELECT 姓名, 模型配置表_ID FROM "官署角色表" WHERE 模型配置表_ID IS NOT NULL LIMIT 3')
print('\n=== Sample Bound ===')
for r in cur.fetchall():
    print(f'  {r[0]}: {r[1]}')

# Check a sample unbound record
cur.execute('SELECT 姓名, 官职 FROM "官署角色表" WHERE 模型配置表_ID IS NULL LIMIT 3')
print('\n=== Sample Unbound ===')
for r in cur.fetchall():
    print(f'  {r[0]}: {r[1]}')

conn.close()
