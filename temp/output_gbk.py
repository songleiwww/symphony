# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

conn = sqlite3.connect(db_path)
conn.text_factory = lambda b: b.decode('gbk', errors='ignore')
cur = conn.cursor()

# Get table names
tables = [t[0] for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall()]

# Find the principles table (64 rows, 5 cols)
for t in tables:
    count = cur.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
    cur.execute(f'PRAGMA table_info("{t}")')
    cols = cur.fetchall()
    
    if count == 64 and len(cols) == 5:
        print(f'Found: {t}')
        print(f'Count: {count}, Columns: {len(cols)}')
        
        # Get rules
        cur.execute(f'SELECT * FROM "{t}" ORDER BY id')
        rules = cur.fetchall()
        
        print(f'\n# 序境系统总则 ({len(rules)}条)\n')
        
        for r in rules:
            print(f'## 第{r[0]}条: {r[1]}')
            print(f'- 规则内容: {r[2]}')
            print(f'- 规则说明: {r[3]}')
            print(f'- 遵循策略: {r[4]}')
            print()
        
        break

conn.close()
