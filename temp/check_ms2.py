#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ModelScope 配置恢复脚本
基于用户提供的API示例
"""
import sqlite3
import os

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = lambda b: b.decode('utf-8', errors='ignore')
cursor = conn.cursor()

# 获取表结构
cursor.execute("PRAGMA table_info(模型配置表)")
columns = cursor.fetchall()
print("模型配置表结构:")
for col in columns:
    print(f"  {col}")

# 查询现有的魔搭/ModelScope模型
print("\n=== 现有ModelScope模型 ===")
cursor.execute("SELECT * FROM 模型配置表 WHERE 服务商 LIKE '%魔搭%' OR 服务商 LIKE '%ModelScope%'")
ms_models = cursor.fetchall()
if ms_models:
    for m in ms_models:
        print(m)
else:
    print("无ModelScope模型配置")

# 查询所有服务商
print("\n=== 所有服务商 ===")
cursor.execute("SELECT DISTINCT 服务商 FROM 模型配置表")
vendors = cursor.fetchall()
for v in vendors:
    print(f"  {v[0]}")

conn.close()
