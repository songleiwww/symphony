# Check models using positional columns
import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# Get total
cur.execute('SELECT COUNT(*) FROM 模型配置表')
print(f'Total models: {cur.fetchone()[0]}')

# Get all data to find status
cur.execute('SELECT * FROM 模型配置表 LIMIT 2')
rows = cur.fetchall()
if rows:
    # Print column names and values
    cur.execute('PRAGMA table_info(模型配置表)')
    cols = cur.fetchall()
    print('\nColumns:')
    for i, c in enumerate(cols):
        print(f'  {i}: {c[1]}')
    
    print('\nSample row:')
    for i, v in enumerate(rows[0]):
        print(f'  {cols[i][1]}: {v}')

conn.close()
