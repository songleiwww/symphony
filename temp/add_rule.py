# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get table info
cur.execute('PRAGMA table_info(系统规则表)')
columns = cur.fetchall()
print('Columns:', [c[1] for c in columns])

# Find the rule name column (usually 2nd)
rule_name_col = columns[1][1]
rule_content_col = columns[2][1]

print(f'Rule name column: {rule_name_col}')
print(f'Rule content column: {rule_content_col}')

# Insert new rule
new_rule_name = "改进优于替换原则"
new_rule_content = """改进现有功能必须基于已有代码，除非无法改进才考虑重构。
开发新功能优先集成到kernel_integration.py统一入口，
不可整体功能分散脱离整体，不可相同功能走两个入口。
新功能必须继承原有架构，渐进式改进为主。"""

sql = f'INSERT INTO "系统规则表" ("{rule_name_col}", "{rule_content_col}") VALUES (?, ?)'
cur.execute(sql, (new_rule_name, new_rule_content))
conn.commit()

print(f'Inserted new rule: {new_rule_name}')

# Verify
cur.execute(f'SELECT * FROM "系统规则表" ORDER BY rowid DESC LIMIT 3')
rows = cur.fetchall()
print('Recent rules:')
for r in rows:
    print(f'  {r}')

conn.close()
