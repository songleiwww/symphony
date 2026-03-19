# -*- coding: utf-8 -*-
import sqlite3

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Get table structure
c.execute("PRAGMA table_info(模型配置表)")
for row in c.fetchall():
    print(row)

conn.close()
