# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Get counts
print('=== Current State ===')
print('模型配置表:', 134, '个模型')
print('官署角色表:', 187, '个角色')

# Check if there's a binding between the two tables
# Check if 官署角色表 has model_id or similar column
cur.execute('PRAGMA table_info("官署角色表")')
cols = cur.fetchall()
print('\n=== 官署角色表 Columns ===')
for c in cols:
    print(f'  {c[1]}: {c[2]}')

# Check model config table
cur.execute('PRAGMA table_info("模型配置表")')
cols2 = cur.fetchall()
print('\n=== 模型配置表 Columns ===')
for c in cols2:
    print(f'  {c[1]}: {c[2]}')

conn.close()
