# -*- coding: utf-8 -*-
import sqlite3
import sys

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

db_path = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db"

# Connect with UTF-8
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Get table info
cur.execute("PRAGMA table_info(模型配置表)")
cols = cur.fetchall()

print("=== Column names ===")
for col in cols:
    print(f"  {col[1]}")

# Try to get a row
cur.execute("SELECT * FROM 模型配置表 LIMIT 1")
row = cur.fetchone()
print("\n=== Sample row ===")
for i, val in enumerate(row):
    print(f"  [{i}] {val}")

conn.close()
