# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get all tables with 64 rows and 5 columns
tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()

# Try to read each table
for tbl in tables:
    try:
        count = cur.execute(f'SELECT COUNT(*) FROM "{tbl[0]}"').fetchone()[0]
        if count == 64:
            cur.execute(f'PRAGMA table_info("{tbl[0]}")')
            cols = cur.fetchall()
            if len(cols) == 5:
                # Try to read as GBK
                try:
                    cur.execute(f'SELECT * FROM "{tbl[0]}" ORDER BY id')
                    rules = cur.fetchall()
                    
                    # Check if first rule contains 序境
                    if rules and '序' in rules[0][1]:
                        print(f'Found correct table: {tbl[0]}')
                        for r in rules[:5]:
                            print(r)
                        break
                except:
                    pass
    except:
        pass

conn.close()
