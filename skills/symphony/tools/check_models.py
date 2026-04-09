# -*- coding: utf-8 -*-
import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\symphony_working.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# List all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print('Tables:', tables)

# Get models table schema
cur.execute("PRAGMA table_info(models)")
print('\nModels schema:')
for row in cur.fetchall():
    print(row)

# Get current models
cur.execute('SELECT provider, model_id, name FROM models LIMIT 20')
print('\nCurrent models:')
for row in cur.fetchall():
    print(row)

conn.close()

