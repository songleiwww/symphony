# -*- coding: utf-8 -*-
"""
添加自进化团队到少府监
"""
import sqlite3
import time

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

now = time.strftime('%Y-%m-%d %H:%M:%S')

# 自进化团队8人 - 添加到少府监
evolution_team = [
    ('evolve_001', '沈清弦', '男', '枢密使', '架构设计、终审决策', '镇国公', 'glm-4.7', '火山引擎', 1),
    ('evolve_002', '陆念昭', '男', '少府监', '统筹调度、任务分发', '开国侯', 'glm-4.7', '火山引擎', 1),
    ('evolve_003', '苏云渺', '男', '工部尚书', '工程实现、安全巡卫', '安定侯', 'Qwen2.5-14B', '硅基流动', 2),
    ('evolve_004', '顾清歌', '男', '翰林学士', '规则制定、文化传承', '文昌侯', 'glm-4-flash', '智谱', 2),
    ('evolve_005', '顾至尊', '男', '首辅大学士', '统筹协调、整合资源', '辅政侯', 'glm-4.7', '火山引擎', 1),
    ('evolve_006', '沈星衍', '男', '智囊博士', '策略规划、意图理解', '智谋伯', 'Qwen2.5-14B', '硅基流动', 2),
    ('evolve_007', '叶轻尘', '男', '行走使', '快速执行、响应迅速', '勤武子', 'glm-4-flash', '智谱', 3),
    ('evolve_008', '林码', '男', '营造司正', '并发处理、GPU加速', '兴业男', 'Qwen2.5-14B', '硅基流动', 3),
]

print(f'Adding {len(evolution_team)} evolution team members...')

for member in evolution_team:
    # id, name, gender, position, duty, title, model, provider, level
    cursor.execute('''
        INSERT OR REPLACE INTO 官属角色表 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (member[0], member[1], member[2], member[3], member[4], member[5], member[6], member[7], member[8], '正常', now, now))

conn.commit()

# 验证
cursor.execute('SELECT COUNT(*) FROM 官属角色表')
total = cursor.fetchone()[0]
print(f'Total officials: {total}')

# 按服务商统计
cursor.execute('SELECT 模型服务商, COUNT(*) as cnt FROM 官属角色表 GROUP BY 模型服务商')
print('\nBy provider:')
for r in cursor.fetchall():
    print(f'  {r[0]}: {r[1]}')

conn.close()
print('\nDone!')
