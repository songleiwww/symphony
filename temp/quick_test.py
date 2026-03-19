# -*- coding: utf-8 -*-
import sys
import os
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

# Check DB
if not os.path.exists(db_path):
    print('DB not found')
    sys.exit(1)

print('=== Test 1: DB Check ===')
print('DB path:', db_path)
print('DB size:', os.path.getsize(db_path)/1024, 'KB')

# Connect DB
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check tables
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in c.fetchall()]
print('Tables:', len(tables))

# Check model config table - try both names
table_name = None
for t in tables:
    if 'model' in t.lower() and 'config' in t.lower():
        table_name = t
        break

if table_name:
    print('Model table:', table_name)
    
    # Try to get columns
    c.execute(f'PRAGMA table_info({table_name})')
    cols = [col[1] for col in c.fetchall()]
    print('Columns:', cols)
    
    # Try to query - find online field
    online_field = None
    for col in cols:
        if 'online' in col.lower() or 'status' in col.lower():
            online_field = col
            break
    
    if online_field:
        c.execute(f'SELECT COUNT(*) FROM {table_name} WHERE {online_field}="online"')
        online = c.fetchone()[0]
        c.execute(f'SELECT COUNT(*) FROM {table_name}')
        total = c.fetchone()[0]
        print('=== Test 2: Models ===')
        print('Total:', total, 'Online:', online)
else:
    print('No model config table found')

# Test dispatcher
print('=== Test 3: Dispatcher ===')
try:
    sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
    from dispatcher import XujingDispatcher
    dispatcher = XujingDispatcher(db_path)
    print('Dispatcher init: OK')
    model = dispatcher.select_model()
    if model:
        print('Select model:', model)
    else:
        print('No model available')
except Exception as e:
    print('Error:', str(e)[:200])

conn.close()
