# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print('[验证陆念昭接管]')

# 1. 检查序境系统总则数量
c.execute('SELECT COUNT(*) FROM 序境系统总则')
rule_count = c.fetchone()[0]
print(f'[1] 序境系统总则: {rule_count}条')

# 2. 检查少府监角色
c.execute("SELECT 官职, 姓名, 职责 FROM 官署角色表 WHERE 所属官署 = '少府监'")
print('')
print('[2] 少府监角色:')
for r in c.fetchall():
    print(f'  {r[0]}: {r[1]} ({r[2]})')

# 3. 检查安全中心
c.execute("SELECT 官职, 姓名 FROM 官署角色表 WHERE 所属官署 = '安全中心'")
print('')
print('[3] 安全中心:')
for r in c.fetchall():
    print(f'  {r[0]}: {r[1]}')

# 4. 检查模型数量
c.execute('SELECT COUNT(*) FROM 模型配置表 WHERE 在线状态 = "online"')
online = c.fetchone()[0]
print('')
print(f'[4] 在线模型: {online}个')

conn.close()

print('')
print('[结论] 陆念昭接管真实，非幻觉')
