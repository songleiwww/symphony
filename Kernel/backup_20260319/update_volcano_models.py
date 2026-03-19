#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新火山引擎模型配置
用户提供的正确模型名称
"""
import sqlite3

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'

# 正确的模型名称映射
model_updates = {
    '豆包 Seed 2.0 Pro': 'doubao-seed-2.0-pro',
    '豆包 Seed 2.0 代码': 'doubao-seed-2.0-code',
    '豆包 Seed 2.0 Lite': 'doubao-seed-2.0-lite',
    'MiniMax M2.5': 'minimax-m2.5',
    '字节GLM-4.7': 'glm-4.7',
    'DeepSeek V3.2': 'deepseek-v3.2',
    'Kimi K2.5': 'kimi-k2.5',
}

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print('=== 更新火山引擎模型配置 ===')
print()

for old_name, new_name in model_updates.items():
    cursor.execute('''
        UPDATE 模型配置表 
        SET 模型名称 = ? 
        WHERE 服务商 = '火山引擎' AND 模型名称 = ?
    ''', (new_name, old_name))
    
    if cursor.rowcount > 0:
        print('Update:', old_name, '->', new_name)
    else:
        print('Not found:', old_name)

# 删除不正确的模型
incorrect_models = ['ABAB 6.5S', 'ABAB 6.5G', 'Kimi Math', 'Kimi Code', '字节GLM-4 Flash', '字节GLM-4V Flash', '通用特效模型']
for name in incorrect_models:
    cursor.execute('''
        DELETE FROM 模型配置表 
        WHERE 服务商 = '火山引擎' AND 模型名称 = ?
    ''', (name,))
    if cursor.rowcount > 0:
        print('Delete:', name)

conn.commit()

# 验证
print()
print('=== 更新后 ===')
cursor.execute('SELECT 模型名称 FROM 模型配置表 WHERE 服务商 = ?', ('火山引擎',))
for row in cursor.fetchall():
    print('-', row[0])

conn.close()
