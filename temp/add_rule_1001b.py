# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find rules table
for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
    count = cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    if count >= 58:
        table_name = t[0]
        
        # Get column count
        cur.execute(f'PRAGMA table_info("{table_name}")')
        cols = cur.fetchall()
        col_count = len(cols)
        print(f'Columns: {col_count}')
        
        # Add rule with all columns
        sql = f'INSERT INTO "{table_name}" VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        new_rule = (
            1001,
            '使用序境模型配置表规则',
            '使用序境自己的模型配置表',
            '每个模型都有API地址和服务商一一对应',
            '汇报/调度等功能必须使用序境模型配置表中的服务商字段',
            '不使用OpenClaw配置',
            '', '', '', '', ''
        )
        try:
            cur.execute(sql, new_rule)
            conn.commit()
            print('Added rule 1001')
        except Exception as e:
            print(f'Error: {e}')
        
        break

conn.close()
