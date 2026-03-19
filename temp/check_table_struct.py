# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print('=== 数据库问题分析 ===\n')

# Get table structures
print('1. 记忆表结构')
cur.execute('PRAGMA table_info("记忆表")')
cols = cur.fetchall()
for c in cols:
    print(f'   {c[1]}: {c[2]}')

print('\n2. 调度历史表结构')
cur.execute('PRAGMA table_info("调度历史表")')
cols = cur.fetchall()
for c in cols:
    print(f'   {c[1]}: {c[2]}')

conn.close()
