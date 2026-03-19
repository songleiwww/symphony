# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find all tables and their exact row counts
print('=== All Tables ===')
for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
    count = cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    if count > 0:
        # Get columns
        cur.execute(f'PRAGMA table_info("{t[0]}")')
        cols = cur.fetchall()
        col_count = len(cols)
        print(f'{t[0]}: {count} rows, {col_count} cols')

conn.close()
