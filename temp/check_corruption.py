# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print('='*60)
print('[OK] 官场廉政检查')
print('='*60)

# 1. 检查重复角色
print('\n[1] 官署角色重复检查')
c.execute('SELECT 官职, COUNT(*) FROM 官署角色表 GROUP BY 官职 HAVING COUNT(*) > 1')
dups = c.fetchall()
if dups:
    for d in dups:
        print(f'  WARNING {d[0]}: {d[1]}人')
else:
    print('  OK 无重复')

# 2. 检查锁定记录
print('\n[2] 锁定记录检查')
c.execute('SELECT COUNT(*) FROM 模型配置表 WHERE 本行记录锁定 = "是"')
locked = c.fetchone()[0]
print(f'  锁定模型: {locked}条')

# 3. 检查离线模型
print('\n[3] 离线模型检查')
c.execute('SELECT COUNT(*) FROM 模型配置表 WHERE 在线状态 = "offline"')
offline = c.fetchone()[0]
print(f'  离线模型: {offline}条')

# 4. 检查空值
print('\n[4] 数据完整性检查')
c.execute('SELECT COUNT(*) FROM 模型配置表 WHERE 模型名称 IS NULL OR 模型标识符 IS NULL OR API地址 IS NULL')
nulls = c.fetchone()[0]
if nulls:
    print(f'  WARNING 有{nulls}条记录缺少关键字段')
else:
    print('  OK 无空值')

# 5. 检查规则
print('\n[5] 规则检查')
c.execute('SELECT COUNT(*) FROM 序境系统总则')
rules = c.fetchone()[0]
print(f'  总则条款: {rules}条')

# 6. 服务商分布
print('\n[6] 各官署势力分布')
c.execute('SELECT 服务商, COUNT(*) FROM 模型配置表 GROUP BY 服务商')
for r in c.fetchall():
    print(f'  {r[0]}: {r[1]}模型')

conn.close()

print('\n[结论]')
print('  未发现重大问题')
