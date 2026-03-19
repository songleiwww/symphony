#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 添加GLM-5到ModelScope (魔搭)
# Column: id, 模型名称, 模型标识, 模型类型, 服务商, API地址, API密钥, 是否启用, 使用场景
try:
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
    print("GLM-5已添加到ModelScope")
except Exception as e:
    print(f"Error: {e}")

# 验证
cursor.execute("SELECT id, 模型名称, 模型标识, 服务商 FROM 模型配置表 WHERE 模型名称='GLM-5'")
print("\nGLM-5配置:")
for m in cursor.fetchall():
    print(f"  ID: {m[0]}, 名称: {m[1]}, 标识: {m[2]}, 服务商: {m[3]}")

# 列出所有魔搭模型
cursor.execute("SELECT id, 模型名称, 模型标识 FROM 模型配置表 WHERE 服务商='魔搭'")
print("\n所有魔搭模型:")
for m in cursor.fetchall():
    print(f"  ID:{m[0]} 名称:{m[1]} 标识:{m[2]}")

conn.close()
