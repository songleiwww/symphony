# -*- coding: utf-8 -*-
import sqlite3
import codecs

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

# Use utf-8 encoding
conn = sqlite3.connect(db_path)
conn.text_factory = lambda b: b.decode('utf-8', errors='ignore')
cur = conn.cursor()

# Find the principles table
for t in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall():
    count = cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    
    if count >= 60:
        table_name = t[0]
        
        # Get all rules
        cur.execute(f'SELECT * FROM "{table_name}" ORDER BY id')
        rules = cur.fetchall()
        
        print(f'# 序境系统总则 ({len(rules)}条)\n')
        
        for r in rules:
            print(f'## 第{r[0]}条: {r[1]}')
            print(f'- 规则内容: {r[2]}')
            print(f'- 规则说明: {r[3]}')
            print(f'- 遵循策略: {r[4]}')
            print()
        
        break

conn.close()
