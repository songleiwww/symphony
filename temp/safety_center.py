# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print('='*60)
print('【安全中心成立计划】')
print('='*60)

# 检查当前模型数量
c.execute('SELECT COUNT(*) FROM 模型配置表')
total = c.fetchone()[0]
print(f'\n当前模型总数: {total}')

# 检查是否有安全相关的官署角色
c.execute("SELECT 官职, 职责 FROM 官署角色表 WHERE 官职 LIKE ? OR 职责 LIKE ?", ('%安全%', '%安全%'))
print('\n【现有安全相关角色】')
rows = c.fetchall()
if rows:
    for r in rows:
        print(f'  {r[0]}: {r[1]}')
else:
    print('  无')

# 检查序境总则中与安全相关的规则
c.execute("SELECT id, 规则名称 FROM 序境系统总则 WHERE 规则名称 LIKE ? OR 规则名称 LIKE ? OR 规则名称 LIKE ?", ('%安全%', '%检测%', '%监督%'))
print('\n【现有安全/检测/监督规则】')
for r in c.fetchall():
    print(f'  第{r[0]}条: {r[1]}')

# 安全模型（可以用于安全检测）
c.execute('SELECT 服务商, COUNT(*) FROM 模型配置表 WHERE 在线状态 = ? GROUP BY 服务商', ('online',))
print('\n【各服务商在线模型】')
for r in c.fetchall():
    print(f'  {r[0]}: {r[1]}')

conn.close()

print('\n【安全中心架构设计】')
print('1. 调度层：操作前安全检测')
print('2. 执行层：风险评估与阻断')
print('3. 监控层：异常行为识别')
print('4. 响应层：自动拦截+日志记录')
