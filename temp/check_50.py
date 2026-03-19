# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find rules table
for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
    count = cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    if count == 53:
        table_name = t[0]
        
        # Get IDs 50-57
        cur.execute(f'SELECT id FROM "{table_name}" WHERE id >= 50 ORDER BY id')
        rows = cur.fetchall()
        print('Rules 50-57:')
        for r in rows:
            print(f'  ID {r[0]}')
        
        break

conn.close()
