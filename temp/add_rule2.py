# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Insert new rule into 系统规则表
new_rule_id = "rule_069"
new_rule_name = "改进优于替换原则"
new_rule_content = "改进现有功能必须基于已有代码，除非无法改进才考虑重构。开发新功能优先集成到kernel_integration.py统一入口，不可整体功能分散脱离整体，不可相同功能走两个入口。新功能必须继承原有架构，渐进式改进为主。"

sql = 'INSERT INTO "系统规则表" (id, 规则名称, 规则内容, 优先级, 状态) VALUES (?, ?, ?, ?, ?)'
cur.execute(sql, (new_rule_id, new_rule_name, new_rule_content, 1, "启用"))
conn.commit()

print(f'Inserted rule: {new_rule_id} - {new_rule_name}')

# Verify
cur.execute('SELECT * FROM "系统规则表" ORDER BY rowid DESC LIMIT 3')
rows = cur.fetchall()
print('Recent rules:')
for r in rows:
    print(f'  {r}')

conn.close()
