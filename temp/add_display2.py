# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find rules table (57 rows)
for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
    cur.execute(f'PRAGMA table_info("{t[0]}")')
    cols = cur.fetchall()
    count = cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    
    if count == 57 and len(cols) == 5:
        table_name = t[0]
        
        # Add rule
        sql = f'INSERT INTO "{table_name}" VALUES (?, ?, ?, ?, ?)'
        new_rule = (
            58,
            '会话展示规则',
            '服务商+模型必须在会话中体现',
            '每次调度在回复中显示服务商名称和模型名称',
            '会话回复格式: [服务商:xxx|模型:xxx]'
        )
        try:
            cur.execute(sql, new_rule)
            conn.commit()
            print('Added rule: 会话展示规则')
        except Exception as e:
            print(f'Error: {e}')
        
        break

conn.close()
