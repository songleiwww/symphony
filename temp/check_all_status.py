# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print('=== All Models Status ===\n')

# Get all models
cur.execute('SELECT "模型名称", "服务商", "状态", "API地址" FROM "模型配置表"')
rows = cur.fetchall()

print('| Model | Provider | Status |')
print('|-------|----------|--------|')
for r in rows:
    print(f'| {r[0]} | {r[1]} | {r[2]} |')

conn.close()
