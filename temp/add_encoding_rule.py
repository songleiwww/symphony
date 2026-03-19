# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Add rule 67 about database encoding
new_rule = (67, '数据库读取规则', '不要设置text_factory，默认UTF-8正确', '子Agent读取数据库时不要设置text_factory', '设置后会导致中文乱码')

cur.execute('INSERT INTO "序境系统总则" VALUES (?, ?, ?, ?, ?)', new_rule)

conn.commit()

# Verify
cur.execute('SELECT COUNT(*) FROM "序境系统总则"')
count = cur.fetchone()[0]
print(f'Total rules: {count}')

conn.close()
