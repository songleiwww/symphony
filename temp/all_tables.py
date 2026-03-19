# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Get all tables with row counts
cur.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cur.fetchall()

print('=== All Database Tables ===\n')
for t in tables:
    tbl = t[0]
    cur.execute(f'SELECT COUNT(*) FROM "{tbl}"')
    count = cur.fetchone()[0]
    print(f'{tbl}: {count} rows')

conn.close()
