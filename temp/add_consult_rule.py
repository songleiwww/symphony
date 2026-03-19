# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Add new rule about consulting other models
new_rule = (66, '模型协商规则', '有拿不准的调用其他模型商量', '多模型协作决策', '调用相关模型讨论后决策')

cur.execute('INSERT INTO "序境系统总则" VALUES (?, ?, ?, ?, ?)', new_rule)

conn.commit()

# Verify
cur.execute('SELECT COUNT(*) FROM "序境系统总则"')
count = cur.fetchone()[0]
print(f'Total rules: {count}')

# Get the new rule
cur.execute('SELECT * FROM "序境系统总则" WHERE id=66')
rule = cur.fetchone()
print(f'New rule: {rule}')

conn.close()
