# -*- coding: utf-8 -*-
import sqlite3
import time

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

now = time.strftime('%Y-%m-%d %H:%M:%S')

# Use raw SQL with position-based update
# Since column names are garbled, let's try using position-based UPDATE
cursor.execute('SELECT * FROM 官属角色表 WHERE id="evolve_002"')
r = cursor.fetchone()
print('Current data positions:')
for i, v in enumerate(r):
    print(f'  [{i}]: {v}')

# The issue is column names are garbled, let's recreate the record
cursor.execute('DELETE FROM 官属角色表 WHERE id="evolve_002"')

# Re-insert with correct data
cursor.execute('''
    INSERT INTO 官属角色表 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    'evolve_002',
    '陆念昭',     # 官名
    '男',         # 性别
    '少府监',     # 职位
    '统筹调度、任务分发、文档归档',  # 职能
    '史官/记录官', # 专长
    'glm-4.7',   # 模型
    '火山引擎',   # 服务商
    1,           # 等级
    '正常',       # 状态
    now,         # 创建时间
    now          # 更新时间
))

conn.commit()

# Verify
cursor.execute('SELECT * FROM 官属角色表 WHERE id="evolve_002"')
r = cursor.fetchone()
print('\nUpdated:')
for i, v in enumerate(r):
    print(f'  [{i}]: {v}')

conn.close()
