# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Query system rules table - use the exact table name from earlier
# Table has 27 rows, 5 columns
table_name = '系统规则表'

print('=== 序境系统总则 ===\n')
print('表结构: id, 规则名称, 规则内容, 规则说明, 遵循策略\n')

cur.execute(f'SELECT * FROM "{table_name}" ORDER BY id')
rows = cur.fetchall()

for row in rows:
    print(f'--- 第{row[0]}条 ---')
    print(f'规则名称: {row[1]}')
    print(f'规则内容: {row[2]}')
    print(f'规则说明: {row[3]}')
    print(f'遵循策略: {row[4]}')
    print()

conn.close()
