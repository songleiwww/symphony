# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get rules from database
cur.execute('SELECT id, "规则名称", "规则配置" FROM "序境系统总则" ORDER BY id')
db_rules = cur.fetchall()

print(f'=== 数据库规则 ({len(db_rules)}条) ===')
for r in db_rules:
    print(f'{r[0]}|{r[1]}|{r[2]}')

conn.close()
