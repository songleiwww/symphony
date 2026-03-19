# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find all tables
print('=== All Tables ===')
for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
    count = cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    if 30 < count < 70:
        # Get column names
        cols = [c[1] for c in cur.execute(f'PRAGMA table_info("{t[0]}")').fetchall()]
        print(f'{t[0]}: {count} rows, cols: {cols[:5]}')

conn.close()
