# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Get all tables
cur.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cur.fetchall()

print('=== All Tables ===')
for t in tables:
    print(t[0])

conn.close()
