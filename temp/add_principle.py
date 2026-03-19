# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find rules table
for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
    cur.execute(f'PRAGMA table_info("{t[0]}")')
    cols = cur.fetchall()
    count = cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    
    if count >= 57 and len(cols) == 5:
        table_name = t[0]
        
        # Add core principle rule
        sql = f'INSERT INTO "{table_name}" VALUES (?, ?, ?, ?, ?)'
        new_rule = (
            1000,
            '多模型协作宗旨',
            '必须多模型工作完成不论简单还是复杂的,只一个模型干的活咱不干',
            '这是序境系统核心宗旨,组合性技术智能体必须发挥多模型协作优势',
            '任何任务优先考虑多模型组合,单模型任务应尽量避免或拆分'
        )
        try:
            cur.execute(sql, new_rule)
            conn.commit()
            print('Added rule 1000: 多模型协作宗旨')
        except Exception as e:
            print(f'Error: {e}')
        
        break

conn.close()
