#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get column names
cursor.execute("PRAGMA table_info(模型配置表)")
cols = cursor.fetchall()
print("Columns:")
for c in cols:
    print(f"  {c[1]}")

# Check existing models with 'GLM'
cursor.execute("SELECT * FROM 模型配置表 WHERE 模型名称 LIKE '%GLM%'")
print("\nGLM models:")
for m in cursor.fetchall():
    print(m)

conn.close()
