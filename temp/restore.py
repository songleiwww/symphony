# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Restore Qwen2.5 Coder to 硅基流动 (it was likely correct before)
cur.execute('UPDATE 模型配置表 SET 服务商="硅基流动" WHERE id="96"')

# Commit
conn.commit()

# Get current state
cur.execute('SELECT id, 模型名称, 服务商, API地址 FROM 模型配置表 WHERE API地址 LIKE "%modelscope%"')
print('=== Current State After Restore ===')
for r in cur.fetchall():
    print(f'ID:{r[0]} | {r[1]} | {r[2]}')

# Get provider counts
cur.execute('SELECT 服务商, COUNT(*) FROM 模型配置表 GROUP BY 服务商')
print('\n=== Provider Counts ===')
for r in cur.fetchall():
    print(f'{r[0]}: {r[1]}')

conn.close()
