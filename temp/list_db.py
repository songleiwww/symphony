# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Get all table names
cur.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = [r[0] for r in cur.fetchall()]

print('=== Database Tables and Columns ===\n')

for table in tables:
    if table.startswith('sqlite'):
        continue
    print(f'## {table}')
    cur.execute(f'PRAGMA table_info("{table}")')
    columns = cur.fetchall()
    for col in columns:
        print(f'  - {col[1]}: {col[2]}')
    print()
    
    # Get row count
    cur.execute(f'SELECT COUNT(*) FROM "{table}"')
    count = cur.fetchone()[0]
    print(f'  Rows: {count}\n')

conn.close()
