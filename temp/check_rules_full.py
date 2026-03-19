# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find all tables
cur.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cur.fetchall()

# Find the rules table - should have 57 rows now
rule_table = None
for t in tables:
    cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"')
    count = cur.fetchone()[0]
    if count == 57:
        rule_table = t[0]
        print(f'Found rules table: {repr(rule_table)} with {count} rows')
        break

if not rule_table:
    # Try to find table with 33 or 57 rows
    for t in tables:
        cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"')
        count = cur.fetchone()[0]
        print(f'{t[0]}: {count} rows')
    exit()

# Get column info
cur.execute(f'PRAGMA table_info("{rule_table}")')
cols = cur.fetchall()
print(f'\nColumns: {len(cols)}')
for c in cols:
    print(f'  {c[1]}: {c[2]}')

# Get rules 1-33
print('\n=== Rules 1-33 (Core) ===')
cur.execute(f'SELECT * FROM "{rule_table}" WHERE id <= 33 ORDER BY id')
for r in cur.fetchall():
    print(f'\n--- {r[0]}: {r[1]} ---')
    print(f'内容: {str(r[2])[:100]}...' if r[2] and len(str(r[2])) > 100 else f'内容: {r[2]}')

conn.close()
