# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Get table names
tables = [t[0] for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall()]

# Find the principles table (64 rows, 5 cols)
for i, t in enumerate(tables):
    count = cur.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
    cur.execute(f'PRAGMA table_info("{t}")')
    cols = cur.fetchall()
    
    if count == 64 and len(cols) == 5:
        print(f'Found principles table at index {i}: {t}')
        print(f'Count: {count}, Columns: {len(cols)}')
        
        # Get rules
        cur.execute(f'SELECT * FROM "{t}" ORDER BY id')
        rules = cur.fetchall()
        
        print(f'\n=== Rules (first 10) ===')
        for r in rules[:10]:
            print(f'{r}')
        
        break

conn.close()
