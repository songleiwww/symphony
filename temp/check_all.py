# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Get all tables
cur.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cur.fetchall()

output = '=== All Database Tables with Full Columns ===\n\n'
for t in tables:
    tbl = t[0]
    # Skip sqlite internal tables
    if tbl.startswith('sqlite'):
        continue
    output += f'## {tbl}\n'
    cur.execute(f'PRAGMA table_info("{tbl}")')
    for col in cur.fetchall():
        output += f'  - {col[1]}: {col[2]}\n'
    output += '\n'

conn.close()

with open(r'C:\Users\Administrator\.openclaw\workspace\memory\all_tables.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Saved to memory/all_tables.txt')
