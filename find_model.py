# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 查找硅基流动和魔搭的模型名称
c.execute("SELECT 模型名称, 模型标识符 FROM 模型配置表 WHERE 服务商='硅基流动' LIMIT 5")
print('【硅基流动】')
for r in c.fetchall():
    print(f'  {r[0]} -> {r[1]}')

c.execute("SELECT 模型名称, 模型标识符 FROM 模型配置表 WHERE 服务商='魔搭' LIMIT 5")
print('\n【魔搭】')
for r in c.fetchall():
    print(f'  {r[0]} -> {r[1]}')

conn.close()
