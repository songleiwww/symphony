# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find rules table (59 rows)
for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
    count = cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    if count == 59:
        # Get column names
        cur.execute(f'PRAGMA table_info("{t[0]}")')
        cols = [c[1] for c in cur.fetchall()]
        print(f'Table: {t[0]}')
        print(f'Columns: {cols}')
        
        # Get last 3 rules
        cur.execute(f'SELECT * FROM "{t[0]}" ORDER BY id DESC LIMIT 5')
        print('=== Last 5 rules ===')
        for r in cur.fetchall():
            print(r)
        
        break

conn.close()
