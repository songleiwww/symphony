# -*- coding: utf-8 -*-
import sqlite3
import sys

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Get table info
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cur.fetchall()]
print('Tables:', tables)

# Get dispatch history columns
if '调度历史表' in tables:
    cur.execute("PRAGMA table_info('调度历史表')")
    cols = [c[1] for c in cur.fetchall()]
    print('Dispatch columns:', cols)
    
    cur.execute('SELECT * FROM "调度历史表" ORDER BY ROWID DESC LIMIT 5')
    rows = cur.fetchall()
    print('Recent records:', rows)

conn.close()
