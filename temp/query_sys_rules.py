# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Try the table with 27 rows - it's the 系统规则表
table_name = '系统规则表'

# Get structure
print('=== Structure ===')
cur.execute(f'PRAGMA table_info("{table_name}")')
for col in cur.fetchall():
    print(f'{col[1]} | {col[2]}')

print('\n=== All Content (27 rows) ===')
cur.execute(f'SELECT * FROM "{table_name}"')
rows = cur.fetchall()

for row in rows:
    print(f'\n--- {row[0]} ---')
    print(f'规则名称: {row[1]}')
    print(f'规则说明: {row[2]}')
    print(f'规则内容: {row[3]}')

conn.close()
