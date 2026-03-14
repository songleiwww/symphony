# -*- coding: utf-8 -*-
import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
c = conn.cursor()

# 查看列名
c.execute('PRAGMA table_info(官属角色表)')
print('官属角色表列名:')
for col in c.fetchall():
    print(f'  {col[1]}')

print()

# 查看数据
c.execute('SELECT * FROM 官属角色表')
rows = c.fetchall()

print('=' * 60)
print('官属角色与模型映射')
print('=' * 60)

for r in rows:
    print(f'ID: {r[0]}')
    print(f'  官名: {r[1]}')
    print(f'  职位: {r[3]}')
    print(f'  模型: {r[6]}')
    print(f'  服务商: {r[7]}')
    print()

conn.close()
