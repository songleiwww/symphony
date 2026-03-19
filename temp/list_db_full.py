# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Get all tables
cur.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = [r[0] for r in cur.fetchall()]

output = '=== 序境系统数据库完整结构 ===\n\n'

for table in tables:
    if table.startswith('sqlite'):
        continue
    output += f'## 【{table}】\n'
    cur.execute(f'PRAGMA table_info("{table}")')
    columns = cur.fetchall()
    for col in columns:
        output += f'  {col[1]}: {col[2]}\n'
    
    cur.execute(f'SELECT COUNT(*) FROM "{table}"')
    count = cur.fetchone()[0]
    output += f'  [记录数: {count}]\n\n'

conn.close()

with open(r'C:\Users\Administrator\.openclaw\workspace\memory\db_structure.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Saved to memory/db_structure.txt')
