# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Add rules created during today
new_rules = [
    (999, '会话展示规则', '服务商+模型必须在会话中体现', '每次调度在回复中显示', '让用户了解真实调度情况'),
    (1000, '多模型协作宗旨', '必须多模型工作完成不论简单还是复杂的,只一个模型干的活咱不干', '这是序境系统核心宗旨', '任何任务优先考虑多模型组合'),
    (1001, '使用序境模型配置表规则', '使用序境自己的模型配置表,每个模型都有API地址和服务商一一对应', '汇报/调度等功能必须使用序境模型配置表中的服务商字段', '不使用OpenClaw配置'),
    (1002, '程序内核适配基准规则', '任何程序内核更改必须以序境数据库为基准', '模型配置表为核心,官署角色表和官署表适配,系统规则表为原则', '程序内核必须遵循数据库规则,自动适配模型配置表变化'),
]

for r in new_rules:
    try:
        cur.execute('INSERT INTO "序境系统总则" VALUES (?, ?, ?, ?, ?)', r)
        print(f'Added rule {r[0]}: {r[1]}')
    except Exception as e:
        print(f'Error adding rule {r[0]}: {e}')

conn.commit()

# Verify
cur.execute('SELECT COUNT(*) FROM "序境系统总则"')
count = cur.fetchone()[0]
print(f'\nTotal rules: {count}')

conn.close()
