# Check model table structure
import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# Get table columns
cur.execute('PRAGMA table_info(模型配置表)')
print('=== Model Config Table Columns ===')
for row in cur.fetchall():
    print(f'{row[1]} ({row[2]})')

# Get all models
print('\n=== All Models ===')
cur.execute('SELECT * FROM 模型配置表 LIMIT 3')
rows = cur.fetchall()
if rows:
    print(f'Found {len(rows)} models (sample):')
    for r in rows:
        print(r)

conn.close()
