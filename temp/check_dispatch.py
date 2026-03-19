import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check all tables
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()

print("=== 数据库所有表 ===\n")
for t in tables:
    print(f"- {t[0]}")

# Check for any usage/history tables
print("\n=== 检查调度相关表 ===")
for t in tables:
    table_name = t[0].lower()
    if any(keyword in table_name for keyword in ['dispatch', 'usage', 'history', 'log', 'call']):
        c.execute(f"SELECT COUNT(*) FROM {t[0]}")
        count = c.fetchone()[0]
        print(f"{t[0]}: {count}条记录")

# Get model info
print("\n=== 模型配置表统计 ===")
c.execute("SELECT 服务商, COUNT(*) FROM 模型配置表 GROUP BY 服务商")
for row in c.fetchall():
    print(f"{row[0]}: {row[1]}个")

conn.close()
