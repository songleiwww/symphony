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
        
        # Get column names
        cur.execute(f'PRAGMA table_info("{table_name}")')
        cols = cur.fetchall()
        col_names = [c[1] for c in cols]
        print(f'Columns: {col_names}')
        
        # Update using index (规则内容 is column 2, 规则说明 is column 3)
        sql = f'UPDATE "{table_name}" SET 规则内容 = ?, 规则说明 = ? WHERE id = 55'
        cur.execute(sql, (
            '同服务商=排队/分布/轮询/哈希,不同服务商=可并发',
            '同商禁止并行(会限流),可用排队/分布/轮询/哈希等非并行方式'
        ))
        conn.commit()
        print('Updated rule 55')
        
        break

conn.close()
