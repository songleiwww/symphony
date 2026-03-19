# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find rules table (54 rows now)
for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
    cur.execute(f'PRAGMA table_info("{t[0]}")')
    cols = cur.fetchall()
    count = cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    
    if count >= 50 and len(cols) == 5:
        table_name = t[0]
        
        # Get max ID
        cur.execute(f'SELECT MAX(id) FROM "{table_name}"')
        max_id = cur.fetchone()[0]
        
        # Add rule about scheduling
        new_rule = (
            max_id + 1,
            '同服务商调度规则',
            '同服务商=排队/分布/轮询,不同服务商=可并发',
            '同商禁止并行(会限流),可用排队/分布/轮询等非并行方式',
            '每次调度前必须确认服务商,同商必须顺序执行'
        )
        
        sql = f'INSERT INTO "{table_name}" VALUES (?, ?, ?, ?, ?)'
        try:
            cur.execute(sql, new_rule)
            conn.commit()
            print(f'Added rule: 同服务商调度规则')
        except Exception as e:
            print(f'Error: {e}')
        
        # Verify
        cur.execute(f'SELECT COUNT(*) FROM "{table_name}"')
        print(f'Total rules: {cur.fetchone()[0]}')
        
        break

conn.close()
