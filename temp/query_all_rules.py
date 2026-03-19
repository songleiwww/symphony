# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Get table structure first
print('=== 系统规则表 结构 ===')
cur.execute('PRAGMA table_info("系统规则表")')
cols = cur.fetchall()
for col in cols:
    print(f'{col[1]}: {col[2]}')

print('\n=== 系统规则表 全部内容 ===')
cur.execute('SELECT * FROM 系统规则表')
rows = cur.fetchall()
for row in rows:
    print(f'\n--- ID: {row[0]} ---')
    for i, col in enumerate(cols):
        val = row[i] if i < len(row) else ''
        if col[1] == '规则内容' or col[1] == '规则说明':
            # Print full content for these columns
            print(f'{col[1]}:')
            print(val)
        else:
            print(f'{col[1]}: {val}')

conn.close()
