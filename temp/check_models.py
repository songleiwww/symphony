# -*- coding: utf-8 -*-
import sqlite3

db_path = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get all columns
cur.execute("PRAGMA table_info(模型配置表)")
cols = [col[1] for col in cur.fetchall()]
print("Columns:", cols)

# Get all models
cur.execute("SELECT * FROM 模型配置表 WHERE 状态='正常'")
rows = cur.fetchall()

print(f"\nTotal models: {len(rows)}")

# Show first few
for row in rows[:3]:
    print("\nSample row:")
    for i, col in enumerate(cols):
        print(f"  {col}: {row[i]}")

conn.close()
