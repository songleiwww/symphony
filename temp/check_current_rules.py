# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find the exact table name
cur.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cur.fetchall()

rule_table = None
for t in tables:
    cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"')
    if cur.fetchone()[0] >= 33:
        rule_table = t[0]
        break

print(f'Found table: {rule_table}')

# Get current rules (1-33) - these are core rules, should NOT be modified
cur.execute(f'SELECT id, 规则名称 FROM "{rule_table}" WHERE id <= 33 ORDER BY id')
print('\n=== Core Rules (1-33) ===')
for r in cur.fetchall():
    print(f'{r[0]}: {r[1]}')

# Get rules > 33 - these are the descriptive table entries we added
cur.execute(f'SELECT id, 规则名称 FROM "{rule_table}" WHERE id > 33 ORDER BY id')
print('\n=== Descriptive Table Entries (34+) ===')
for r in cur.fetchall():
    print(f'{r[0]}: {r[1]}')

conn.close()
