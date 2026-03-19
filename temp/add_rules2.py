# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find the exact table name
cur.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cur.fetchall()

rule_table = None
for t in tables:
    cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"')
    if cur.fetchone()[0] == 27:
        rule_table = t[0]
        break

if not rule_table:
    print('Could not find rules table')
    exit()

print(f'Found table: {rule_table}')

# Get current max ID
cur.execute(f'SELECT MAX(id) FROM "{rule_table}"')
max_id = cur.fetchone()[0]
print(f'Current max ID: {max_id}')

# New rules to add
new_rules = [
    (28, '智能体规则优化建议规则', '优化建议需要评估影响，重大变更需用户确认后才能执行', '智能体优化建议规则', '遵循第31条批量修改确认规则'),
    (29, '多模型调度规则', '同服务商顺序排队执行，不同服务商可并发执行', '多模型调度核心规则', '使用sessions_spawn并行调度'),
    (30, '配置默认规则', '默认指向序境系统内核，非OpenClaw', '配置文件规则', '确保配置指向正确'),
    (31, '数据库修改防范规则', '批量修改前必须确认、修改前备份、字段先行验证', '数据库安全规则', '遵循第12条模型配置表修改原则'),
    (32, '记忆同步规则', '数据库优先，定期同步，禁止固化记忆', '记忆同步规则', '每次会话启动自动检测变化'),
    (33, '多模型调度协作规则', '使用sessions_spawn调度，不同服务商并行，同服务商排队，角色分配，结果汇总', '多模型协作规则', '遵循第29条调度规则'),
]

# Check existing IDs
cur.execute(f'SELECT id FROM "{rule_table}"')
existing_ids = [r[0] for r in cur.fetchall()]
print(f'Existing IDs: {existing_ids}')

# Insert new rules
for rule in new_rules:
    if rule[0] not in existing_ids:
        cur.execute(f'INSERT INTO "{rule_table}" (id, 规则名称, 规则内容, 规则说明, 遵循策略) VALUES (?, ?, ?, ?, ?)', rule)
        print(f'Added rule {rule[0]}: {rule[1]}')
    else:
        print(f'Rule {rule[0]} already exists')

conn.commit()

# Verify
cur.execute(f'SELECT id, 规则名称 FROM "{rule_table}" ORDER BY id')
print('\n=== Updated Rules (33 total) ===')
for r in cur.fetchall():
    print(f'{r[0]}: {r[1]}')

conn.close()
