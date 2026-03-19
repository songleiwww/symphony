#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加ModelScope GLM-5模型
"""
import sqlite3
import os

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = lambda b: b.decode('utf-8', errors='ignore')
cursor = conn.cursor()

# 检查GLM-5是否已存在
print("=== 检查GLM-5模型 ===")
cursor.execute("SELECT * FROM 模型配置表 WHERE 模型名称 LIKE '%GLM-5%' OR 模型标识 LIKE '%GLM-5%'")
glm_models = cursor.fetchall()
if glm_models:
    print("GLM-5已存在:")
    for m in glm_models:
        print(m)
else:
    print("GLM-5不存在，需要添加")
    
    # 添加GLM-5模型
    cursor.execute("""
        INSERT INTO 模型配置表 (模型名称, 模型标识, 模型类型, 服务商, API地址, API密钥, 是否启用, 使用场景)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'GLM-5',
        'ZhipuAI/GLM-5',
        '通义对话',
        '魔搭',
        'https://api-inference.modelscope.cn/v1',
        'ms-eac6f154-3502-4721-a168-ce7caeaf1033',
        '是',
        '通用对话'
    ))
    conn.commit()
    print("GLM-5模型已添加")

# 列出所有ModelScope模型
print("\n=== 所有魔搭/ModelScope模型 ===")
cursor.execute("SELECT id, 模型名称, 模型标识, 使用场景 FROM 模型配置表 WHERE 服务商='魔搭'")
for m in cursor.fetchall():
    print(f"  ID:{m[0]} 名称:{m[1]} 标识:{m[2]} 场景:{m[3]}")

conn.close()
