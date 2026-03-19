# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get all table names
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()

# Find model config table
for t in tables:
    if '模型' in t[0] and '配置' in t[0]:
        print(f'Found: {t[0]}')
        
        # Get all columns
        cur.execute(f'PRAGMA table_info("{t[0]}")')
        cols = cur.fetchall()
        
        # Find status column (contains '状态')
        status_col = None
        for c in cols:
            if '状态' in c[1]:
                status_col = c[1]
                print(f'Status column: {status_col}')
                break
        
        if status_col:
            cur.execute(f'SELECT {status_col}, COUNT(*) FROM "{t[0]}" GROUP BY {status_col}')
            for row in cur.fetchall():
                print(f'{row[0]}: {row[1]}')
        break

conn.close()
