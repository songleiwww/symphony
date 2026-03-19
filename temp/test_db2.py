# -*- coding: utf-8 -*-
import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

# Try different approaches
print('=== Test 1: Default connection ===')
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute('SELECT * FROM "序境系统总则" WHERE id=1')
row = cur.fetchone()
print(f'Default: {row}')
conn.close()

print('\n=== Test 2: With text_factory str ===')
conn = sqlite3.connect(db_path)
conn.text_factory = str
cur = conn.cursor()
cur.execute('SELECT * FROM "序境系统总则" WHERE id=1')
row = cur.fetchone()
print(f'str: {row}')
conn.close()

print('\n=== Test 3: With GBK ===')
conn = sqlite3.connect(db_path)
conn.text_factory = lambda b: b.decode('gbk', errors='ignore')
cur = conn.cursor()
cur.execute('SELECT * FROM "序境系统总则" WHERE id=1')
row = cur.fetchone()
print(f'GBK: {row}')
conn.close()

print('\n=== Test 4: Check raw bytes ===')
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute('SELECT id, "规则名称" FROM "序境系统总则" WHERE id=1')
row = cur.fetchone()
print(f'Raw: id={row[0]}, name={repr(row[1])}')
conn.close()
