# Check for API key rules in database
import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# Get column names for rules table
cur.execute('PRAGMA table_info(系统规则表)')
cols = cur.fetchall()
print('=== Rules Table Columns ===')
for c in cols:
    print(f'  {c[1]}')

# Search for API/Key related rules
print('\n=== Searching for API/Key rules ===')
cur.execute('SELECT id, 规则名称, 规则内容 FROM 系统规则表')
for row in cur.fetchall():
    content = str(row[2]) if row[2] else ''
    name = str(row[1]) if row[1] else ''
    if 'api' in content.lower() or 'key' in content.lower() or '密钥' in content or 'API' in name or '密钥' in name:
        print(f'{row[0]}: {name}')
        print(f'  {content[:100]}...')

conn.close()
