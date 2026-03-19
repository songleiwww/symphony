# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get all table names
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()

# Find model config table
model_table = None
for t in tables:
    if '模型配置' in t[0]:
        model_table = t[0]
        print(f'Found model table: {model_table}')
        
        # Get status column
        cur.execute(f'PRAGMA table_info("{model_table}")')
        cols = cur.fetchall()
        for c in cols:
            print(f'  {c[1]}: {c[2]}')
        
        # Get status counts
        print('\nStatus counts:')
        cur.execute(f'SELECT 状态, COUNT(*) FROM "{model_table}" GROUP BY 状态')
        for row in cur.fetchall():
            print(f'  {row[0]}: {row[1]}')
        break

conn.close()
