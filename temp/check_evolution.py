# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\evolution.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()

print('=== evolution.db 表 ===')
for t in tables:
    print(f'- {t[0]}')
    cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"')
    count = cur.fetchone()[0]
    print(f'  {count}条')

conn.close()
