# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Find rules table
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cur.fetchall()]

rules_table = None
for t in tables:
    if '规则' in t or 'ϵͳ' in t:
        print(f'Found table: {t}')
        rules_table = t
        break

if rules_table:
    # Insert new rule about evolution method
    new_rule_id = "rule_070"
    new_rule_name = "功能进化原则"
    new_rule_content = "开发新功能必须先分析原有功能模块：1.分析原有功能是否可改进；2.有改进则基于原有代码进化；3.无法改进才考虑重构或新开发；4.禁止做一个扔一个的开发方式；5.每次改进需记录版本变更日志。"
    
    sql = f'INSERT INTO "{rules_table}" (id, 规则名称, 规则内容, 优先级, 状态) VALUES (?, ?, ?, ?, ?)'
    try:
        cur.execute(sql, (new_rule_id, new_rule_name, new_rule_content, 1, "启用"))
        conn.commit()
        print(f'Success! Inserted rule: {new_rule_id}')
    except Exception as e:
        print(f'Error: {e}')

# Also update MEMORY.md
print('\n=== Evolution Rule Added ===')
print('Rule 070: 功能进化原则')
print('1. 分析原有功能是否可改进')
print('2. 有改进则基于原有代码进化')
print('3. 无法改进才考虑重构或新开发')
print('4. 禁止做一个扔一个的开发方式')
print('5. 每次改进需记录版本变更日志')

conn.close()
