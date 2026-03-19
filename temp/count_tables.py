# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find all tables with their counts
cur.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cur.fetchall()

for t in tables:
    cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"')
    count = cur.fetchone()[0]
    if count > 30:
        print(f'{t[0]}: {count} rows')

conn.close()
