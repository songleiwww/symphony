# -*- coding: utf-8 -*-
import sqlite3
conn = sqlite3.connect('C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db')
c = conn.cursor()

# Get table info - check exact column names
c.execute("PRAGMA table_info('模型配置表')")
cols = c.fetchall()
print("Table columns:")
for col in cols:
    print(f"  Index {col[0]}: '{col[1]}'")

# Try using column index 2 (model identifier)
c.execute("SELECT * FROM 模型配置表 WHERE id = '12'")
row = c.fetchone()
print(f"\nCurrent ID 12 row:")
print(f"  Index 0 (id): {row[0]}")
print(f"  Index 1 (name): {row[1]}")
print(f"  Index 2 (model_id): {row[2]}")

conn.close()
