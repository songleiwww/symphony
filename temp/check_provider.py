# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Check model config columns
cur.execute("PRAGMA table_info('模型配置表')")
cols = [c[1] for c in cur.fetchall()]
print('Model config columns:', cols)

# Get provider info for dispatch models
models = ['doubao-seed-2.0-pro', 'ark-code-latest', 'deepseek-v3.2']
for m in models:
    cur.execute(f'SELECT * FROM "模型配置表" WHERE "模型名称" = ?', (m,))
    r = cur.fetchone()
    if r:
        print(f'\n{m}:')
        for i, c in enumerate(cols):
            print(f'  {c}: {r[i]}')

conn.close()
