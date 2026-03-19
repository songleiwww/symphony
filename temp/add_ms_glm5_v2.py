#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
db = sqlite3.connect('C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db')
c = db.cursor()

# Get column info first
c.execute('PRAGMA table_info(模型配置表)')
cols = [row[1] for row in c.fetchall()]
print("Columns:", cols)

# Add GLM-5 using explicit columns
c.execute('''INSERT INTO 模型配置表 (id, 模型名称, 模型标识, 模型类型, 服务商, API地址, API密钥, 是否启用, 使用场景) 
             VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
    ('GLM-5', 'ZhipuAI/GLM-5', '通义对话', '魔搭', 'https://api-inference.modelscope.cn/v1', 'ms-eac6f154-3502-4721-a168-ce7caeaf1033', '是', '通用对话'))
db.commit()
print('GLM-5 added to ModelScope')

# Verify
c.execute('SELECT * FROM 模型配置表 WHERE 模型名称=?', ('GLM-5',))
row = c.fetchone()
if row:
    print("Verification - GLM-5:")
    for i, col in enumerate(cols):
        print(f"  {col}: {row[i]}")
else:
    print("Error: GLM-5 not found")

db.close()
