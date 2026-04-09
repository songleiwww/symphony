# -*- coding: utf-8 -*-
import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony_working.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# List all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print('Tables:', tables)

# Check model_config schema
for t in tables:
    name = t[0]
    if 'model' in name.lower():
        cur.execute(f"PRAGMA table_info({name})")
        print(f'\n{name} schema:')
        for row in cur.fetchall():
            print(row)
        cur.execute(f"SELECT COUNT(*) FROM {name}")
        print(f'Count: {cur.fetchone()[0]}')

conn.close()

