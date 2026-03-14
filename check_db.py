# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get table info
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", [t[0] for t in tables])

# Try to get all from a known table
for table in tables:
    tname = table[0]
    cursor.execute(f"SELECT * FROM {tname} LIMIT 3")
    cols = [d[0] for d in cursor.description]
    print(f"\n{tname} columns: {cols}")
    rows = cursor.fetchall()
    print(f"Rows: {len(rows)}")

conn.close()
