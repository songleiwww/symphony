# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find table with name containing 序境系统总则
print('=== All tables ===')
for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
    print(t[0])

conn.close()
