# -*- coding: utf-8 -*-
import sqlite3

old_db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\symphony.db'
new_db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony_working.db'

for label, db_path in [('鏃у簱 symphony.db', old_db), ('鏂板簱 symphony_working.db', new_db)]:
    conn = sqlite3.connect(db_path)
    conn.text_factory = str
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(model_config)")
    print(f'\n=== {label} model_config schema ===')
    for row in cur.fetchall():
        print(f'  {row}')
    # Sample a few rows
    cur.execute('SELECT * FROM model_config LIMIT 2')
    print(f'\n  Sample rows:')
    for row in cur.fetchall():
        print(f'  {row}')
    conn.close()

