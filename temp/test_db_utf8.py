# -*- coding: utf-8 -*-
import sqlite3
import sys
import io

# Fix console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

print('=== Test Database Encoding ===\n')

# Test reading with utf-8
try:
    conn = sqlite3.connect(db_path)
    conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
    cur = conn.cursor()
    
    # Find the principles table
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    all_tables = cur.fetchall()
    
    for t in all_tables:
        if '序境' in t[0] or '规则' in t[0]:
            print(f'Found table: {t[0]}')
            
            # Read rules
            cur.execute(f'SELECT * FROM "{t[0]}" ORDER BY id LIMIT 5')
            rules = cur.fetchall()
            
            for r in rules:
                print(f'  {r}')
            break
    
    conn.close()
except Exception as e:
    print(f'Error: {e}')

print('\n=== Test Model Config Table ===')

try:
    conn = sqlite3.connect(db_path)
    conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
    cur = conn.cursor()
    
    # Find model config table
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    all_tables = cur.fetchall()
    
    for t in all_tables:
        if '模型配置' in t[0]:
            print(f'Found table: {t[0]}')
            
            # Read sample
            cur.execute(f'SELECT * FROM "{t[0]}" LIMIT 3')
            models = cur.fetchall()
            
            for m in models:
                print(f'  {m}')
            break
    
    conn.close()
except Exception as e:
    print(f'Error: {e}')
