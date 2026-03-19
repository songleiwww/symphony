# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Query all tables that might contain rules
print('=== 序境系统总则相关表 ===\n')

# 1. 内核规则表
print('## 内核规则表')
cur.execute('SELECT * FROM 内核规则表 ORDER BY 优先级')
for row in cur.fetchall():
    print(f'ID: {row[0]}')
    print(f'名称: {row[1]}')
    print(f'内容: {row[2][:100]}...' if row[2] and len(row[2]) > 100 else f'内容: {row[2]}')
    print(f'优先级: {row[3]}')
    print(f'状态: {row[4]}')
    print('---')

# 2. 调度历史表
print('\n## 调度历史表')
cur.execute('SELECT * FROM 调度历史表 LIMIT 5')
for row in cur.fetchall():
    print(row)

# 3. 系统配置表
print('\n## 系统配置表')
cur.execute('SELECT * FROM 系统配置表')
for row in cur.fetchall():
    print(f'ID: {row[0]}')
    print(f'配置名称: {row[1]}')
    print(f'配置值: {row[2]}')
    print('---')

conn.close()
