import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Search for glm5
c.execute("SELECT * FROM 模型配置表 WHERE 模型标识符 LIKE '%glm%' OR 模型名称 LIKE '%glm%'")
rows = c.fetchall()

print("=== 搜索GLM模型 ===\n")
if rows:
    for row in rows:
        print(f"ID {row[0]}: {row[1]} = {row[2]}")
else:
    print("未找到GLM模型")

# Also check ID 15 current value
c.execute("SELECT * FROM 模型配置表 WHERE id = '15'")
row = c.fetchone()
print(f"\nID 15当前值: {row[1]} = {row[2]}")

conn.close()
