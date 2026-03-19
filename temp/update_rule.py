# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find rules table
for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
    count = cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    if count == 55:
        table_name = t[0]
        
        # Update rule 55 with hash
        cur.execute(f'''
            UPDATE "{table_name}"
            SET 规则内容 = '同服务商=排队/分布/轮询/哈希,不同服务商=可并发',
                规则说明 = '同商禁止并行(会限流),可用排队/分布/轮询/哈希等非并行方式'
            WHERE id = 55
        ''')
        conn.commit()
        print('Updated rule 55 with 哈希')
        
        break

conn.close()
