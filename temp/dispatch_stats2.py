import sqlite3
from datetime import datetime, timedelta

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check dispatch history table
print("=== 调度历史表 ===\n")

# Get recent records
c.execute("""
    SELECT * FROM 调度历史表 
    ORDER BY id DESC 
    LIMIT 20
""")
rows = c.fetchall()

print(f"总记录数: {len(rows)}")
if rows:
    print("\n表结构(第一条记录):")
    for i, val in enumerate(rows[0]):
        print(f"  列{i}: {val}")

# Get statistics
print("\n=== 调度统计 ===")

# Total
c.execute("SELECT COUNT(*) FROM 调度历史表")
total = c.fetchone()[0]
print(f"总调度次数: {total}")

# By model
print("\n按模型统计 (Top 10):")
c.execute("""
    SELECT model_name, COUNT(*) as 次数, SUM(success) as 成功
    FROM 调度历史表
    GROUP BY model_name
    ORDER BY 次数 DESC
    LIMIT 10
""")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]}次 (成功{row[2]})")

# Success rate
c.execute("SELECT SUM(success), COUNT(*) FROM 调度历史表")
stats = c.fetchone()
if stats[1]:
    rate = (stats[0] / stats[1]) * 100
    print(f"\n总成功率: {rate:.1f}%")

conn.close()
