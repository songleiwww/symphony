# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Verify rules
cur.execute('SELECT * FROM "序境系统总则" ORDER BY id')
rules = cur.fetchall()

print(f'=== 序境系统总则验证 ({len(rules)}条) ===\n')

for r in rules[:10]:
    print(f'第{r[0]}条: {r[1]}')
    print(f'  规则配置: {r[2]}')
    print(f'  规则说明: {r[3]}')
    print(f'  智能体操作规范: {r[4]}')
    print()

print(f'...共{len(rules)}条')

conn.close()
