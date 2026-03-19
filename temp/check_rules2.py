# -*- coding: utf-8 -*-
import sqlite3
import sys

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Get all tables
cur.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cur.fetchall()

for t in tables:
    tbl = t[0]
    if 'rule' in tbl.lower() or '规则' in tbl:
        print(f'\n=== TABLE: {tbl} ===')
        cur.execute(f'PRAGMA table_info("{tbl}")')
        cols = []
        for col in cur.fetchall():
            print(f'  {col[1]}: {col[2]}')
            cols.append(col[1])
        
        # Show 2 samples
        cur.execute(f'SELECT * FROM "{tbl}" LIMIT 2')
        for i, row in enumerate(rows):
            print(f'  Row {i+1}: {row}')

conn.close()
