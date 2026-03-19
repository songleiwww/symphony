# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find rules table
for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
    count = cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    if count >= 59:
        table_name = t[0]
        
        # Add rule with all columns
        sql = f'INSERT INTO "{table_name}" VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        new_rule = (
            1002,
            '程序内核适配基准规则',
            '任何程序内核更改必须以序境数据库为基准',
            '模型配置表为核心,官署角色表和官署表适配,系统规则表为原则',
            '程序内核必须遵循数据库规则,自动适配模型配置表变化',
            'Skills工具需调整相关文件,去掉无用信息,保证指向正确',
            '', '', '', '', ''
        )
        try:
            cur.execute(sql, new_rule)
            conn.commit()
            print('Added rule 1002')
        except Exception as e:
            print(f'Error: {e}')
        
        break

conn.close()
