# -*- coding: utf-8 -*-
import sqlite3, os

bases = [
    r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony_working.db',
    r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony_kernel.db',
    r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\symphony.db',
    r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony_backup_20260329_113916.db',
    r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\backup\model_registry_20260404_174724.db',
]

for db_path in bases:
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [t[0] for t in cur.fetchall()]
            model_count = 0
            if 'model_config' in tables:
                cur.execute('SELECT COUNT(*) FROM model_config')
                model_count = cur.fetchone()[0]
            conn.close()
            print(f'{os.path.basename(db_path):50} tables={tables} model_count={model_count}')
        except Exception as e:
            print(f'{db_path}: ERROR {e}')
    else:
        print(f'{db_path}: FILE NOT FOUND')

