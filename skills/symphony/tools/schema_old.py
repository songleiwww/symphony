# -*- coding: utf-8 -*-
import sqlite3

old_db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\symphony.db'
conn = sqlite3.connect(old_db)
conn.text_factory = str
cur = conn.cursor()
cur.execute("PRAGMA table_info(model_config)")
print('symphony.db model_config schema:')
for row in cur.fetchall():
    print(row)
conn.close()

