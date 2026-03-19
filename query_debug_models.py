# -*- coding: utf-8 -*-
import sqlite3
import sys

conn = sqlite3.connect('data/symphony.db')
conn.text_factory = str
cursor = conn.cursor()

# 查询有code能力的模型
cursor.execute("SELECT 官职, 姓名, 模型 FROM 官署角色表 WHERE 模型 LIKE '%code%' OR 模型 LIKE '%Code%' OR 官职 LIKE '%工部%' OR 官职 LIKE '%翰林%'")
results = cursor.fetchall()
for r in results:
    print(f"{r[0]}: {r[1]} - {r[2]}")

conn.close()
