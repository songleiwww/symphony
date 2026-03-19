# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
c = conn.cursor()

# Update models with modelscope API to 魔搭 provider
c.execute('SELECT id, 模型名称, API地址 FROM 模型配置表 WHERE API地址 LIKE "%modelscope%"')
rows = c.fetchall()

print('=== Before Update ===')
for r in rows:
    print(f'ID:{r[0]} Name:{r[1]} URL:{r[2]}')

# Update to 魔搭
updated = 0
for r in rows:
    model_id = r[0]
    c.execute('UPDATE 模型配置表 SET 服务商=? WHERE id=?', ('魔搭', model_id))
    updated += 1

conn.commit()

# Verify
print('\n=== After Update ===')
c.execute('SELECT id, 模型名称, 服务商, API地址 FROM 模型配置表 WHERE 服务商="魔搭"')
rows = c.fetchall()
for r in rows:
    print(f'ID:{r[0]} Name:{r[1]} Provider:{r[2]} URL:{r[3]}')

print(f'\n=== Updated {updated} records ===')
conn.close()
