# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# List tables
print('=== 官署角色表结构 ===')
cur.execute('PRAGMA table_info("官署角色表")')
cols = cur.fetchall()
for c in cols:
    print(f'{c[1]}: {c[2]}')

print('\n=== 序境系统总则 ===')
cur.execute('SELECT COUNT(*) FROM "序境系统总则"')
print(f'总规则数: {cur.fetchone()[0]}')

conn.close()
