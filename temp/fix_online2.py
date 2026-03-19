# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get table info
cur.execute('PRAGMA table_info(模型配置表)')
columns = cur.fetchall()
print('Columns:', [c[1] for c in columns])

# Find status column (last one)
status_col = columns[-1][1]
print(f'Status column: {status_col}')

# Update all models to online
sql = f'UPDATE "模型配置表" SET "{status_col}" = "online"'
print(f'Executing: {sql}')
cur.execute(sql)
conn.commit()

print(f'Updated {cur.rowcount} models to online')

conn.close()
