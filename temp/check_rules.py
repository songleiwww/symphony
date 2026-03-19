# -*- coding: utf-8 -*-
import sqlite3
db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Get 系统规则表 structure
print('=== 系统规则表 ===')
cur.execute('PRAGMA table_info("系统规则表")')
for col in cur.fetchall():
    print(f'{col[1]}: {col[2]}')

# Get sample data
print('\n=== Sample Data ===')
cur.execute('SELECT * FROM "系统规则表" LIMIT 3')
rows = cur.fetchall()
for row in rows:
    print(row)

conn.close()
