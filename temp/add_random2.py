# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find rules table (55 rows)
for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
    count = cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    if count == 55:
        table_name = t[0]
        
        # Add new rule about random
        sql = f'INSERT INTO "{table_name}" VALUES (?, ?, ?, ?, ?)'
        new_rule = (60, '同服务商调度-随机', '随机', '同服务商可用随机方式避开并发', '同商禁止并行,随机分配请求')
        try:
            cur.execute(sql, new_rule)
            conn.commit()
            print('Added rule 60: 随机')
        except Exception as e:
            print(f'Error: {e}')
        
        # Verify
        cur.execute(f'SELECT COUNT(*) FROM "{table_name}"')
        print(f'Total: {cur.fetchone()[0]}')
        
        break

conn.close()
