# -*- coding: utf-8 -*-
import sqlite3

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
c = conn.cursor()

# 获取所有数据
c.execute('SELECT id, 模型名称, 服务商, 是否启用 FROM 模型配置表 LIMIT 10')
rows = c.fetchall()

print('ID  模型名称                    服务商     是否启用')
print('-' * 60)
for row in rows:
    print(f'{row[0]:<3} {row[1]:<24} {row[2]:<9} {row[3]}')

# 统计启用状态
c.execute('SELECT 是否启用, COUNT(*) FROM 模型配置表 GROUP BY 是否启用')
print('\n启用状态统计:')
for row in c.fetchall():
    print(f'  {row[0]}: {row[1]}')

conn.close()
