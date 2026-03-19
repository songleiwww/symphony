# -*- coding: utf-8 -*-
import sqlite3

db_path = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get table schema
cur.execute("PRAGMA table_info(模型配置表)")
print("=== 模型配置表 columns ===")
for col in cur.fetchall():
    print(f"  {col[1]}")

conn.close()
