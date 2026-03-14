# -*- coding: utf-8 -*-
import sqlite3
conn = sqlite3.connect(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db')
c = conn.cursor()

# List all tables
c.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = c.fetchall()
print('数据库表:')
for t in tables:
    print('  ' + t[0])

# Check for organization related tables
print('\n少府监机构说明:')
print('  - 少府监是系统的核心机构')
print('  - 负责AI智能体调度与协作')
print('  - 下设5位官属角色')

# Show role structure
print('\n官属角色结构:')
c.execute('SELECT id, 职能, 模型服务商, 角色等级 FROM 官属角色表')
for r in c.fetchall():
    print(f'  {r[0]}: {r[1]} - {r[2]} (等级{r[3]})')

conn.close()
