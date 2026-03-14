#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect(r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db")
cursor = conn.cursor()

# 检查表结构
cursor.execute("PRAGMA table_info(模型配置表)")
print("Table columns:")
for col in cursor.fetchall():
    print(f"  {col[1]}")

print("\n\nAvailable models:")
cursor.execute('SELECT 模型名称, 服务商 FROM 模型配置表 WHERE 是否在线="在线" LIMIT 15')
for r in cursor.fetchall():
    print(f"  {r[1]}: {r[0]}")

conn.close()
