# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find rules table (53 rows)
for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
    count = cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    if count == 53:
        table_name = t[0]
        
        # Get ID 54
        cur.execute(f'SELECT * FROM "{table_name}" WHERE id = 54')
        row = cur.fetchone()
        print('Rule 54:', row)
        
        break

conn.close()
