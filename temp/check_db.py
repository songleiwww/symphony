# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Get all table names
cur.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = [r[0] for r in cur.fetchall()]
print('=== Database Tables ===')
for t in tables:
    print(f'- {t}')

# Get model config table structure
cur.execute('PRAGMA table_info(模型配置表)')
print('\n=== Model Config Table Columns ===')
for r in cur.fetchall():
    print(f'{r[1]}: {r[2]}')

# Get provider counts
cur.execute('SELECT 服务商, COUNT(*) FROM 模型配置表 GROUP BY 服务商')
print('\n=== Provider Counts ===')
for r in cur.fetchall():
    print(f'{r[0]}: {r[1]}')

conn.close()
