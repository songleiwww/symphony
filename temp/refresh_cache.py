# -*- coding: utf-8 -*-
import sqlite3
import os
import json

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
cache_file = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\temp\rules_cache.json'

# Force refresh cache
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()

# Find rules table
cur.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cur.fetchall()

rule_table = None
for t in tables:
    cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"')
    if cur.fetchone()[0] >= 33:
        rule_table = t[0]
        break

if rule_table:
    cur.execute(f'SELECT * FROM "{rule_table}" ORDER BY id')
    rules = cur.fetchall()
    cur.execute(f'PRAGMA table_info("{rule_table}")')
    cols = [c[1] for c in cur.fetchall()]
    
    cache = {
        'table': rule_table,
        'columns': cols,
        'rules_count': len(rules),
        'rules': [(r[0], r[1], r[2]) for r in rules]  # id, name, content
    }
    
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

conn.close()

print(f'=== 已读取总则 ===')
print(f'表: {cache["table"]}')
print(f'规则数: {cache["rules_count"]}')
print(f'缓存已刷新')
