#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

DB_PATH = r"C:\Users\Administrator\.openclaw\skills\symphony\data\symphony_working.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=== All volcano models ===")
cursor.execute("""
    SELECT id, name, model_id, provider_name, status 
    FROM model_config 
    WHERE provider_name = 'volcano' AND status = 'active'
""")
rows = cursor.fetchall()

for row in rows:
    print(f"  id={row[0]}: {row[1]} - {row[2]} ({row[3]}) status={row[4]}")

print("\n=== The newly added activity model ===")
cursor.execute("""
    SELECT id, name, model_id, api_key 
    FROM model_config 
    WHERE id = 32
""")
row = cursor.fetchone()
if row:
    print(f"  id: {row[0]}")
print(f"  name: {row[1]}")
print(f"  model_id: {row[2]}")
print(f"  api_key: {row[3][:8]}... (masked)")

conn.close()
