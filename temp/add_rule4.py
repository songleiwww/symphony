# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find rules table (53 rows)
for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
    count = cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    if count == 53:
        table_name = t[0]
        
        # Insert using 5 columns
        sql = f'INSERT INTO "{table_name}" VALUES (?, ?, ?, ?, ?)'
        new_rule = (
            54,
            '模型服务商正确名称',
            '英伟达:106个, 火山引擎:8个, 魔搭:7个, 智谱:7个, 硅基流动:6个',
            'MiniMax不是服务商,是模型名,调度必须使用数据库中实际服务商名称',
            '使用前必须读取模型配置表确认服务商'
        )
        
        try:
            cur.execute(sql, new_rule)
            conn.commit()
            print(f'Added rule 54')
        except Exception as e:
            print(f'Error: {e}')
        
        # Verify
        cur.execute(f'SELECT COUNT(*) FROM "{table_name}"')
        print(f'Total: {cur.fetchone()[0]}')
        
        break

conn.close()
