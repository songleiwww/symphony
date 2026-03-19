# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Check models with ModelScope URL
cur.execute('SELECT id, 模型名称, 服务商, API地址 FROM 模型配置表 WHERE API地址 LIKE "%modelscope%"')
print('=== Models with ModelScope URL ===')
for r in cur.fetchall():
    print(f'ID:{r[0]} | Name:{r[1]} | Provider:{r[2]} | URL:{r[3]}')

conn.close()
