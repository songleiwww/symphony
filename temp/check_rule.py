# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find rules table
for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
    count = cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    if count >= 58:
        table_name = t[0]
        
        # Find rule 1000
        cur.execute(f'SELECT * FROM "{table_name}" WHERE id = 1000')
        r = cur.fetchone()
        if r:
            print(f'Rule 1000: {r}')
        
        break

conn.close()
