# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get doubao info
cur.execute('SELECT * FROM "模型配置表" WHERE "模型名称" LIKE "%doubao%"')
r = cur.fetchone()
if r:
    cols = ['id', 'model_name', 'model_id', 'model_type', 'provider', 'api_url', 'api_key', 'enabled', 'use_case', 'created_at', 'updated_at', 'context_records', 'multi_record', 'status']
    print('doubao-seed-2.0-pro:')
    for i, c in enumerate(cols):
        print(f'  {c}: {r[i]}')

conn.close()
