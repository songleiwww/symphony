# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find model config table (134 rows)
for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
    count = cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    if count == 134:
        table_name = t[0]
        
        # Get all providers
        cur.execute(f'SELECT DISTINCT 服务商 FROM "{table_name}"')
        providers = cur.fetchall()
        print('=== All Providers in Model Config ===')
        for p in providers:
            print(f'  - {p[0]}')
        
        # Count by provider
        cur.execute(f'SELECT 服务商, COUNT(*) FROM "{table_name}" GROUP BY 服务商')
        print('\n=== Count by Provider ===')
        for p in cur.fetchall():
            print(f'  {p[0]}: {p[1]}')
        
        break

conn.close()
