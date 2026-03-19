# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Add new rule about cache mechanism
new_rule = (65, '缓存刷新规则', '可依赖缓存，更新时刷新', '用户要求增加/修改规则后刷新缓存', '非强制每次读取数据库')

cur.execute('INSERT INTO "序境系统总则" VALUES (?, ?, ?, ?, ?)', new_rule)

conn.commit()

# Verify
cur.execute('SELECT COUNT(*) FROM "序境系统总则"')
count = cur.fetchone()[0]
print(f'Total rules: {count}')

# Get the new rule
cur.execute('SELECT * FROM "序境系统总则" WHERE id=65')
rule = cur.fetchone()
print(f'New rule: {rule}')

conn.close()
