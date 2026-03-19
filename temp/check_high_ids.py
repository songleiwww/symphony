# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Check existing rules with high IDs
cur.execute('SELECT id, "规则名称" FROM "序境系统总则" WHERE id >= 50 ORDER BY id')
rules = cur.fetchall()

print('=== 当前高ID规则 ===')
for r in rules:
    print(f'{r[0]}: {r[1]}')

conn.close()
