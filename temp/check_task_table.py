import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
c = conn.cursor()

# Get task table structure
c.execute("PRAGMA table_info(任务表)")
print("=== 任务表结构 ===")
for col in c.fetchall():
    print(f"  {col[1]}: {col[2]}")

# Get all tasks
print("\n=== 所有任务 ===")
c.execute("SELECT * FROM 任务表")
for row in c.fetchall():
    print(f"  {row}")

conn.close()
