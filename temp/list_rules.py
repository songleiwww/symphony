# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find the principles table (the one with 5 columns)
for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
    cur.execute(f'PRAGMA table_info("{t[0]}")')
    cols = cur.fetchall()
    count = cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    
    if count >= 50 and len(cols) == 5:
        table_name = t[0]
        
        # Get all current rules
        cur.execute(f'SELECT * FROM "{table_name}" ORDER BY id')
        rules = cur.fetchall()
        
        print(f'=== Current Rules in 序境系统总则 ({count} rules) ===')
        for r in rules:
            print(f'{r[0]}: {r[1]}')
        
        break

conn.close()
