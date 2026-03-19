# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find table with 59 rows (the one we thought was 系统规则表)
print('=== Tables with 59 rows ===')
for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
    count = cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    if count == 59:
        print(f'Found: {t[0]} ({count} rows)')
        
        # Get columns
        cur.execute(f'PRAGMA table_info("{t[0]}")')
        cols = cur.fetchall()
        print(f'Columns: {len(cols)}')
        for c in cols:
            print(f'  - {c[1]}')
        
        # Get first row
        cur.execute(f'SELECT * FROM "{t[0]}" LIMIT 1')
        row = cur.fetchone()
        print(f'First row: {row}')

conn.close()
