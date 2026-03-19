# -*- coding: utf-8 -*-
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

# Test different encodings
encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16', 'latin1']

print('=== 测试数据库编码 ===\n')

for enc in encodings:
    try:
        conn = sqlite3.connect(db_path)
        conn.text_factory = lambda b: b.decode(enc, errors='ignore')
        cur = conn.cursor()
        
        # Try to read table name
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 5")
        tables = cur.fetchall()
        
        print(f'✓ {enc}: 读取成功')
        for t in tables[:3]:
            try:
                print(f'  - {t[0]}')
            except:
                print(f'  - [编码错误]')
        
        conn.close()
    except Exception as e:
        print(f'✗ {enc}: {e}')

print('\n=== 测试序境系统总则表 ===')

# Test reading with utf-8
try:
    conn = sqlite3.connect(db_path)
    conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
    cur = conn.cursor()
    
    # Find the principles table
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    all_tables = cur.fetchall()
    
    for t in all_tables:
        if '序境系统总则' in t[0]:
            print(f'找到表: {t[0]}')
            
            # Read rules
            cur.execute(f'SELECT * FROM "{t[0]}" ORDER BY id LIMIT 5')
            rules = cur.fetchall()
            
            for r in rules:
                print(f'  {r}')
            break
    
    conn.close()
except Exception as e:
    print(f'错误: {e}')
