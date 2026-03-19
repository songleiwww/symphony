import sqlite3
from datetime import datetime, timedelta

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check dispatch history table
print("=== 调度历史表 ===\n")

# Get table schema
c.execute("PRAGMA table_info(调度历史表)")
columns = c.fetchall()
print("表结构:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Get recent records
c.execute("""
    SELECT * FROM 调度历史表 
    ORDER BY id DESC 
    LIMIT 20
""")
rows = c.fetchall()

print(f"\n最近20条记录 ({len(rows)}条):")
for row in rows[:10]:
    print(f"  {row}")

# Get statistics
print("\n=== 调度统计 ===")

# Today
today = datetime.now().strftime('%Y-%m-%d')
c.execute(f"SELECT COUNT(*) FROM 调度历史表 WHERE 创建时间 LIKE '{today}%'")
today_count = c.fetchone()[0]
print(f"今日调度次数: {today_count}")

# This week
week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
c.execute(f"SELECT COUNT(*) FROM 调度历史表 WHERE 创建时间 >= '{week_ago}'")
week_count = c.fetchone()[0]
print(f"本周调度次数: {week_count}")

# Total
c.execute("SELECT COUNT(*) FROM 调度历史表")
total = c.fetchone()[0]
print(f"总调度次数: {total}")

# By provider
print("\n按服务商统计:")
c.execute("""
    SELECT m.服务商, COUNT(*) as 次数
    FROM 调度历史表 d
    JOIN 模型配置表 m ON d.模型ID = m.id
    GROUP BY m.服务商
    ORDER BY 次数 DESC
""")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]}次")

conn.close()
