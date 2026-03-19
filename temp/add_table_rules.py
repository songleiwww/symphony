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
    if cur.fetchone()[0] == 33:
        rule_table = t[0]
        break

print(f'Found table: {rule_table}')

# Get column names
cur.execute(f'PRAGMA table_info("{rule_table}")')
cols = cur.fetchall()
col_names = [c[1] for c in cols]

# Tables to add (useful but not core)
# Core: 内核规则表, 模型配置表, 官署角色表
# To add: other useful tables as descriptions

new_rules = [
    (34, 'MCP服务表', 'MCP服务配置表，存储MCP服务信息', 'MCP服务表字段：id, 服务名称, 服务地址, 状态, 创建时间', '用于MCP服务管理'),
    (35, 'MCP配置表', 'MCP客户端配置表', 'MCP配置表字段：id, 配置名称, 配置值, 描述', 'MCP连接配置'),
    (36, 'Skill持久化表', 'Skill技能持久化存储', 'Skill持久化表字段：id, Skill名称, 版本, 配置, 状态', 'Skill管理'),
    (37, 'Token认证表', 'Token认证信息', 'Token认证表字段：token_id, token_hash, token_type, name, quota, is_active', 'API Token管理'),
    (38, 'Token使用日志表', 'Token使用记录', 'Token使用日志表字段：id, token_id, used_at, endpoint, success', '使用统计'),
    (39, '调度历史表', '模型调度历史记录', '调度历史表字段：id, task_id, role_id, model_name, score, success, timestamp', '调度分析'),
    (40, '对话轮次表', '对话会话管理', '对话轮次表字段：id, session_id, 用户ID, 模型ID, 开始时间, 结束时间', '会话管理'),
    (41, '功能建议表', '用户功能建议', '功能建议表字段：id, 建议内容, 状态, 创建时间', '反馈收集'),
    (42, '官署表', '官署组织结构', '官署表字段：id, 名称, 级别, 职位, 官品, 职责, 父级, 状态', '组织架构'),
    (43, '记忆表', '记忆存储', '记忆表字段：memory_id, content, memory_type, importance, source, tags, created_at', '记忆系统'),
    (44, '接管状态表', '系统接管状态', '接管状态表字段：id, 状态, 接管时间, 持续时间', '系统状态'),
    (45, '开发计划表', '开发任务计划', '开发计划表字段：id, 计划名称, 内容, 优先级, 状态, 截止日期', '项目管理'),
    (46, '模型标签表', '模型标签分类', '模型标签表字段：id, 标签名, 描述, 创建时间', '模型分类'),
    (47, '模型参数表', '模型参数配置', '模型参数表字段：id, 模型ID, 参数名, 参数值', '参数管理'),
    (48, '模型打分表', '模型评分记录', '模型打分表字段：id, 模型ID, 评分, 评价, 时间', '模型评估'),
    (49, '模型权重表', '模型权重配置', '模型权重表字段：id, 模型ID, 权重值, 用途', '调度权重'),
    (50, '模型执行结果表', '模型执行结果', '模型执行结果表字段：id, task_id, 模型ID, 结果, 耗时, 状态', '执行记录'),
    (51, '内核调试说明表', '内核调试文档', '内核调试说明表字段：id, 标题, 说明内容, 优先级, 状态', '调试文档'),
    (52, '任务表', '任务管理', '任务表字段：task_id, content, task_type, priority, status, created_at', '任务系统'),
    (53, '任务会话表', '任务与会话关联', '任务会话表字段：id, task_id, session_id, 状态', '任务会话'),
    (54, '限制规则表', '系统限制规则', '限制规则表字段：id, 规则名称, 限制内容, 优先级, 状态', '限制管理'),
    (55, '专家模型池表', '专家模型池', '专家模型池表字段：id, 能力分类, 模型, 引擎, API地址, 评分', '专家模型'),
    (56, '用户交流技能表', '用户交互技能', '用户交流技能表字段：id, 技能名称, 描述, 触发词, 状态', '交互技能'),
    (57, '引导安装配置表', '引导安装配置', '引导安装配置表字段：id, 配置项, 配置值, 描述', '安装配置'),
]

# Get existing IDs
cur.execute(f'SELECT id FROM "{rule_table}"')
existing_ids = [r[0] for r in cur.fetchall()]
print(f'Current max ID: {max(existing_ids) if existing_ids else 0}')

# Insert new rules
added = 0
for rule in new_rules:
    if rule[0] not in existing_ids:
        sql = f'INSERT INTO "{rule_table}" VALUES (?, ?, ?, ?, ?)'
        cur.execute(sql, rule)
        added += 1

conn.commit()

# Verify
cur.execute(f'SELECT COUNT(*) FROM "{rule_table}"')
print(f'Total rules now: {cur.fetchone()[0]}')
print(f'Added {added} new rules')

conn.close()
