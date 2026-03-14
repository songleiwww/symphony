# -*- coding: utf-8 -*-
import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
c = conn.cursor()

print('=' * 70)
print('少府监官属人员情况')
print('=' * 70)

# 查看所有官属
c.execute('SELECT id, 官名, 职位, 职能, 模型名称, 模型服务商, 角色等级, 状态 FROM 官属角色表')
rows = c.fetchall()

print(f'\n共 {len(rows)} 位官属\n')

for r in rows:
    print(f'【{r[1]}】')
    print(f'  ID: {r[0]}')
    print(f'  职位: {r[2]}')
    print(f'  职能: {r[3]}')
    print(f'  模型: {r[4]} ({r[5]})')
    print(f'  等级: {r[6]}')
    print(f'  状态: {r[7]}')
    print()

conn.close()
