# -*- coding: utf-8 -*-
import sqlite3
db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Get Token related tables
cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name LIKE "%Token%"')
tables = cur.fetchall()
print('=== Token Related Tables ===')
for t in tables:
    print(f'\n## {t[0]}')
    cur.execute(f'PRAGMA table_info("{t[0]}")')
    for col in cur.fetchall():
        print(f'  {col[1]}: {col[2]}')
    
    # Get sample data
    cur.execute(f'SELECT * FROM "{t[0]}" LIMIT 1')
    row = cur.fetchone()
    if row:
        print(f'  Sample: {row}')

conn.close()
