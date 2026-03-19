# -*- coding: utf-8 -*-
import sqlite3
import json

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
c = conn.cursor()

# Get table structure
c.execute('PRAGMA table_info("模型配置表")')
cols = c.fetchall()
print("=== Table Structure ===")
for col in cols:
    print(f"{col[1]}: {col[2]}")

# Find models with modelscope in API URL but different provider
print("\n=== Models with ModelScope API URL ===")
c.execute('SELECT id, 模型名称, 服务商, API地址 FROM 模型配置表 WHERE API地址 LIKE "%modelscope%"')
rows = c.fetchall()
for r in rows:
    print(f"ID:{r[0]} Name:{r[1]} Provider:{r[2]} URL:{r[3]}")

# Check if there's a provider field we can update
print("\n=== Checking for update capability ===")
c.execute('SELECT id, 模型名称, 服务商 FROM 模型配置表 WHERE 服务商="硅基流动" LIMIT 3')
rows = c.fetchall()
for r in rows:
    print(f"ID:{r[0]} Name:{r[1]} Provider:{r[2]}")

conn.close()
print("\n=== Done ===")
