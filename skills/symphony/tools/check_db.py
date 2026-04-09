# -*- coding: utf-8 -*-
import sqlite3
import os

db_files = [
    r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\symphony.db',
    r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony_kernel.db',
    r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
]

for db_path in db_files:
    print('=== ' + db_path + ' ===')
    print('Exists: ' + str(os.path.exists(db_path)))
    if os.path.exists(db_path) and os.path.getsize(db_path) > 0:
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cur.fetchall()
            print('Tables: ' + str([t[0] for t in tables]))
            for t in tables:
                cur.execute('PRAGMA table_info(' + t[0] + ')')
                cols = [c[1] for c in cur.fetchall()]
                print('  ' + t[0] + ' columns: ' + str(cols))
                cur.execute('PRAGMA index_list(' + t[0] + ')')
                indexes = cur.fetchall()
                print('  ' + t[0] + ' indexes: ' + str([idx[1] for idx in indexes]))
            conn.close()
        except Exception as e:
            print('Error: ' + str(e))
    else:
        print('Empty or not accessible')
    print()

