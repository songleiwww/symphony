# Check online models
import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# Get total count
cur.execute('SELECT COUNT(*) FROM 模型配置表')
total = cur.fetchone()[0]
print(f'Total models: {total}')

# Get status counts - try different column names
cur.execute('PRAGMA table_info(模型配置表)')
cols = cur.fetchall()
status_col = None
for c in cols:
    if '状态' in c[1]:
        status_col = c[1]
        break

if status_col:
    cur.execute(f'SELECT {status_col}, COUNT(*) FROM 模型配置表 GROUP BY {status_col}')
    for row in cur.fetchall():
        print(f'{row[0]}: {row[1]}')

# Get sample online model
print('\n=== Sample Online Model ===')
cur.execute('SELECT * FROM 模型配置表 WHERE 运行状态 = "online" LIMIT 1')
row = cur.fetchone()
if row:
    print(f'Found online model: {row[1]}')

conn.close()
