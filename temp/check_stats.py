# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print('[精确统计]')

# 模型统计
c.execute('SELECT COUNT(*) FROM 模型配置表')
model_count = c.fetchone()[0]
print(f'模型总数: {model_count}')

c.execute('SELECT COUNT(*) FROM 模型配置表 WHERE 在线状态 = "online"')
online_count = c.fetchone()[0]
print(f'在线模型: {online_count}')

# 规则统计
c.execute('SELECT COUNT(*) FROM 序境系统总则')
rule_count = c.fetchone()[0]
print(f'规则总数: {rule_count}')

# 官署统计
c.execute('SELECT COUNT(*) FROM 官署角色表')
role_count = c.fetchone()[0]
print(f'官署角色: {role_count}')

# 各服务商模型数
c.execute('SELECT 服务商, COUNT(*) FROM 模型配置表 GROUP BY 服务商')
print('\n[各服务商模型数]')
for r in c.fetchall():
    print(f'  {r[0]}: {r[1]}')

conn.close()
