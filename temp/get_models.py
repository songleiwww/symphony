# -*- coding: utf-8 -*-
import sqlite3

db_path = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get all data without filtering by status
cur.execute("SELECT * FROM 模型配置表")
rows = cur.fetchall()

# Get column names
cur.execute("PRAGMA table_info(模型配置表)")
cols_info = cur.fetchall()
cols = [c[1] for c in cols_info]

# Print first 3 rows
print(f"Total rows: {len(rows)}")
print(f"Columns ({len(cols)}): {cols}")

# Find index of key columns
print("\n=== Finding key columns ===")
for i, col in enumerate(cols):
    print(f"  [{i}] {col}")

conn.close()
