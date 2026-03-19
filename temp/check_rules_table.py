# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print('Tables:', [t[0] for t in tables])

# Check for rules table
for table in tables:
    if '规则' in table[0]:
        print(f'\nTable: {table[0]}')
        cur.execute(f'PRAGMA table_info({table[0]})')
        cols = cur.fetchall()
        print('Columns:', [c[1] for c in cols])
        
        # Get recent rows
        cur.execute(f'SELECT * FROM {table[0]} ORDER BY rowid DESC LIMIT 3')
        rows = cur.fetchall()
        print('Recent rows:', rows)

conn.close()
