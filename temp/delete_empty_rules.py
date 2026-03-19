# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find the rules table
cur.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cur.fetchall()

rule_table = None
for t in tables:
    cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"')
    if cur.fetchone()[0] == 57:
        rule_table = t[0]
        break

if rule_table:
    # Delete empty rows (18, 19, 20, 21) - where 规则名称 is empty
    cur.execute(f'DELETE FROM "{rule_table}" WHERE id IN (18, 19, 20, 21) AND (规则名称 IS NULL OR 规则名称 = "")')
    deleted = cur.rowcount
    conn.commit()
    
    print(f'Deleted {deleted} empty rows')
    
    # Verify
    cur.execute(f'SELECT COUNT(*) FROM "{rule_table}"')
    print(f'Total rules now: {cur.fetchone()[0]}')

conn.close()
