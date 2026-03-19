# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find the rules table (57 rows)
cur.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cur.fetchall()

rule_table = None
for t in tables:
    cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"')
    if cur.fetchone()[0] == 57:
        rule_table = t[0]
        break

if rule_table:
    # Get first 5 rules as quick check
    cur.execute(f'SELECT id, 规则名称, 规则内容 FROM "{rule_table}" WHERE id <= 5')
    print('=== 已读取序境系统总则（数据库） ===')
    for r in cur.fetchall():
        print(f'{r[0]}: {r[1]}')

conn.close()
