import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
c = conn.cursor()

# Check all tables
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in c.fetchall()]

print('=== 数据库表 ===')
for t in tables:
    print(f'  {t}')

# Check for user data
print('\n=== 任务表 ===')
c.execute('SELECT * FROM 任务表')
for row in c.fetchall():
    print(f'  {row}')

# Check 官署角色表 for user/official data
print('\n=== 官署角色表 ===')
c.execute('SELECT id, 姓名, 官职, 所属官署, 状态 FROM 官署角色表')
for row in c.fetchall():
    print(f'  {row}')

conn.close()
