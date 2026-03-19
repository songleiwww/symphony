import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute("UPDATE 任务表 SET status = 'pending'")
conn.commit()
print(f'Reset {c.rowcount} tasks to pending')
conn.close()
