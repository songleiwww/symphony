# -*- coding: utf-8 -*-
import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
cur = conn.cursor()

# List all tables with row counts
print('=== All Tables ===\n')
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
all_tables = cur.fetchall()

for t in all_tables:
    try:
        cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"')
        count = cur.fetchone()[0]
        if count > 0:
            print(f'{t[0]}: {count} rows')
    except:
        pass

print('\n=== Find Rules Table (50-70 rows) ===')

for t in all_tables:
    try:
        cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"')
        count = cur.fetchone()[0]
        if 50 <= count <= 70:
            print(f'\nFound: {t[0]} ({count} rows)')
            
            # Get columns
            cur.execute(f'PRAGMA table_info("{t[0]}")')
            cols = cur.fetchall()
            print('Columns:', [c[1] for c in cols])
            
            # Get first row
            cur.execute(f'SELECT * FROM "{t[0]}" LIMIT 2')
            rows = cur.fetchall()
            for r in rows:
                print(f'  {r}')
    except:
        pass

conn.close()
