# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get officials and their models
print('=== 少府监核心官员模型配置 ===\n')

# Find role bindings
cur.execute('''
SELECT r."官署角色名称", m."模型标识符", m."API地址", m."服务商" 
FROM "官署角色表" r
LEFT JOIN "模型配置表" m ON r."模型配置ID" = m."id"
WHERE r."官署角色名称" IN ('少府监', '枢密使', '首辅大学士', '工部尚书', '翰林学士', '智囊博士')
ORDER BY r."id"
''')

results = cur.fetchall()
for r in results:
    print(f'{r[0]}: {r[1]} ({r[3]})')

print('\n=== 序境系统总则统计 ===')
cur.execute('SELECT COUNT(*) FROM "序境系统总则"')
print(f'总规则数: {cur.fetchone()[0]}')

conn.close()
