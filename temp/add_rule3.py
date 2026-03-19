# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# List all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cur.fetchall()]

# Find rules table
rules_table = None
for t in tables:
    if '规则' in t or 'ϵͳ' in t:
        print(f'Found table: {t}')
        rules_table = t
        break

if rules_table:
    # Insert new rule
    new_rule_id = "rule_069"
    new_rule_name = "改进优于替换原则"
    new_rule_content = "改进现有功能必须基于已有代码，除非无法改进才考虑重构。开发新功能优先集成到kernel_integration.py统一入口，不可整体功能分散脱离整体，不可相同功能走两个入口。新功能必须继承原有架构，渐进式改进为主。"
    
    sql = f'INSERT INTO "{rules_table}" (id, 规则名称, 规则内容, 优先级, 状态) VALUES (?, ?, ?, ?, ?)'
    try:
        cur.execute(sql, (new_rule_id, new_rule_name, new_rule_content, 1, "启用"))
        conn.commit()
        print(f'Success! Inserted rule: {new_rule_id}')
    except Exception as e:
        print(f'Error: {e}')
        # Try alternative columns
        cur.execute(f'PRAGMA table_info({rules_table})')
        cols = cur.fetchall()
        print('Columns:', [c[1] for c in cols])
else:
    print('Rules table not found')

conn.close()
