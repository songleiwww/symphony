# -*- coding: utf-8 -*-
import sqlite3
conn = sqlite3.connect(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db')
c = conn.cursor()

print('=' * 60)
print('少府监机构情况')
print('=' * 60)

# 查看所有表
c.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = [r[0] for r in c.fetchall()]
print(f'\n数据库表: {tables}')

# 查看官属角色
print('\n少府监官属:')
c.execute('SELECT 官名, 职位, 角色等级 FROM 官属角色表')
for r in c.fetchall():
    print(f'  {r[0]}: {r[1]} (等级{r[2]})')

conn.close()
