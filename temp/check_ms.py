#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
import os

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = lambda b: b.decode('utf-8', errors='ignore')
cursor = conn.cursor()

# Get table list
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", tables)

# Get model config - check column names
cursor.execute("SELECT * FROM sqlite_master WHERE type='table' AND name LIKE '%model%'")
print("\nModel tables:", cursor.fetchall())

conn.close()
