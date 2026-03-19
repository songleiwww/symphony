# -*- coding: utf-8 -*-
import sqlite3
import os

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cursor = conn.cursor()

# Find model-related tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%模型%' OR name LIKE '%model%')")
tables = cursor.fetchall()
print("Model tables:", [t[0] for t in tables])

# Query model configuration
for table in tables:
    try:
        cursor.execute(f'PRAGMA table_info("{table[0]}")')
        cols = [c[1] for c in cursor.fetchall()]
        print(f"\n{table[0]} columns: {cols}")
        
        cursor.execute(f'SELECT * FROM "{table[0]}" LIMIT 5')
        rows = cursor.fetchall()
        for row in rows:
            print(f"  {row}")
    except Exception as e:
        print(f"Error {table[0]}: {e}")

conn.close()
