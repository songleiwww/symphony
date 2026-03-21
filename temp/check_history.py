# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print('[调度历史表检查]')

# 检查调度历史表结构
c.execute("PRAGMA table_info(调度历史表)")
columns = c.fetchall()
print('\n[调度历史表字段]')
for col in columns:
    print(f'  {col[1]}: {col[2]}')

# 检查是否有记录
c.execute('SELECT COUNT(*) FROM 调度历史表')
count = c.fetchone()[0]
print(f'\n[调度历史记录数]: {count}')

if count > 0:
    c.execute('SELECT * FROM 调度历史表 ORDER BY ROWID DESC LIMIT 5')
    records = c.fetchall()
    print('\n[最近5条记录]')
    for r in records:
        print(f'  {r}')

# 检查任务表
print('\n[任务表检查]')
c.execute('SELECT COUNT(*) FROM 任务表')
task_count = c.fetchone()[0]
print(f'[任务记录数]: {task_count}')

conn.close()

print('\n[结论] 需要建立Token使用记录机制')
