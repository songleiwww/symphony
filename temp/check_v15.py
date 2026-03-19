import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check current status of ID 6
c.execute("SELECT * FROM 模型配置表 WHERE id = '6'")
row = c.fetchone()
print(f"=== ID 6 当前状态 ===")
print(f"模型: {row[1]}")
print(f"ID: {row[2]}")

# Check if it was already updated to v1.5
if "v1.5" in row[2]:
    print("\n✅ 已更新为 v1.5 版本")
    print("用户刚才测试的是 v1.5 版本")
else:
    print(f"\n当前版本: {row[2]}")

conn.close()
