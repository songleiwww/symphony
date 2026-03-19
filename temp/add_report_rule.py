# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find rules table
for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
    count = cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    if count == 56:
        table_name = t[0]
        
        # Get max id
        cur.execute(f'SELECT MAX(id) FROM "{table_name}"')
        max_id = cur.fetchone()[0]
        
        # Add rule about reporting
        sql = f'INSERT INTO "{table_name}" VALUES (?, ?, ?, ?, ?)'
        new_rule = (
            max_id + 1,
            '调度汇报规则',
            '服务商+模型名+Tokens计算',
            '每次调度必须汇报服务商、模型名称、Tokens消耗，方便用户了解真实效果',
            '调度汇报=服务商名称|模型名称|输入Tokens|输出Tokens|总Tokens'
        )
        try:
            cur.execute(sql, new_rule)
            conn.commit()
            print('Added rule: 调度汇报规则')
        except Exception as e:
            print(f'Error: {e}')
        
        break

conn.close()
