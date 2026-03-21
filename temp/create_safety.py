# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print('='*60)
print('[OK] Safety Center')
print('='*60)

# 1. Add safety roles
print('\n[1] Add safety roles')
c.execute("SELECT id FROM 官署角色表 ORDER BY id DESC LIMIT 1")
last_role_id = c.fetchone()[0]
num = int(last_role_id.split('-')[1]) + 1

safety_roles = [
    (f'role-{num}', '安全尚书', '安全尚书', '安全中心', '统筹安全,风险检测', 1, 'active'),
    (f'role-{num+1}', '安全侍郎', '安全侍郎', '安全中心', '风险评估,阻断决策', 1, 'active'),
    (f'role-{num+2}', '安全监丞', '安全监丞', '安全中心', '异常识别,行为监控', 1, 'active'),
    (f'role-{num+3}', '安全录事', '安全录事', '安全中心', '日志记录,自动拦截', 1, 'active'),
]

for role in safety_roles:
    c.execute('''
        INSERT INTO 官署角色表 (id, 姓名, 官职, 所属官署, 职责, 角色等级, 状态)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', role)
    print(f'  OK {role[2]}')

# 2. Add safety rules
print('\n[2] Add safety rules')
c.execute('SELECT MAX(id) FROM 序境系统总则')
max_rule_id = c.fetchone()[0]

safety_rules = [
    (max_rule_id+1, '安全中心规则', 
     '1.调度层:操作前检测 2.执行层:风险评估 3.监控层:异常识别 4.响应层:自动拦截',
     '安全中心架构'),
    (max_rule_id+2, '风险阻断原则', 
     '1.高风险:立即阻断 2.中风险:需确认 3.低风险:放行 4.无风险:直接放行',
     '风险分级'),
    (max_rule_id+3, '安全检测性能', 
     '1.检测<100ms 2.不影响流畅 3.异步+同步 4.异常降级',
     '性能保障'),
]

for rule in safety_rules:
    c.execute('''
        INSERT INTO 序境系统总则 (id, 规则名称, 规则配置, 规则说明)
        VALUES (?, ?, ?, ?)
    ''', rule)
    print(f'  OK {rule[1]}')

conn.commit()
conn.close()
print('\n[OK] Safety Center established')
