# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Get model identifiers
cur.execute('SELECT 模型标识符, 服务商 FROM "模型配置表" LIMIT 10')
print('=== Available Models ===')
for r in cur.fetchall():
    print(f'{r[1]}: {r[0]}')

conn.close()
