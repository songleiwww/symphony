# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find rules table (55 rows)
for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
    count = cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    if count == 55:
        table_name = t[0]
        
        # Get max id
        cur.execute(f'SELECT MAX(id) FROM "{table_name}"')
        max_id = cur.fetchone()[0]
        print(f'Max ID: {max_id}')
        
        break

conn.close()
