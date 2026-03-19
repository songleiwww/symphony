# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find the principles table
for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
    cur.execute(f'PRAGMA table_info("{t[0]}")')
    cols = cur.fetchall()
    count = cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    
    if count >= 60 and len(cols) == 5:
        table_name = t[0]
        
        # Get all rules - show raw
        cur.execute(f'SELECT * FROM "{table_name}" ORDER BY id')
        rules = cur.fetchall()
        
        print(f'=== Raw Rules from Database ===')
        for r in rules[:10]:  # First 10
            print(f'ID: {r[0]}')
            print(f'  Col1: {repr(r[1])}')
            print(f'  Col2: {repr(r[2])}')
            print(f'  Col3: {repr(r[3])}')
            print(f'  Col4: {repr(r[4])}')
            print()
        
        break

conn.close()
