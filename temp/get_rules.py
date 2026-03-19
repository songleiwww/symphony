# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Get all tables and find the one with 27 rows
cur.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cur.fetchall()

# Find rules table (the one with 27 rows)
for t in tables:
    cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"')
    count = cur.fetchone()[0]
    if count == 27:
        table_name = t[0]
        print(f'Found table: {table_name} with {count} rows')
        
        # Get structure
        cur.execute(f'PRAGMA table_info("{table_name}")')
        cols = cur.fetchall()
        print('\nColumns:')
        for c in cols:
            print(f'  {c[1]}: {c[2]}')
        
        # Get all data
        print('\n=== Content ===')
        cur.execute(f'SELECT * FROM "{table_name}" ORDER BY id')
        rows = cur.fetchall()
        
        for row in rows:
            print(f'\n--- 第{row[0]}条 ---')
            for i, c in enumerate(cols):
                if i < len(row):
                    val = str(row[i])[:100] if row[i] else ''
                    print(f'{c[1]}: {val}')
        break

conn.close()
