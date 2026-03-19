import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Search for minimax in NVIDIA models
c.execute("SELECT * FROM 模型配置表 WHERE 模型标识符 LIKE '%minimax%' AND 服务商 = '英伟达'")
rows = c.fetchall()

print("=== 英伟达中的Minimax模型 ===")
if rows:
    for row in rows:
        print(f"ID {row[0]}: {row[1]} = {row[2]}")
else:
    print("未找到")

# Get ID 42 current value
c.execute("SELECT * FROM 模型配置表 WHERE id = '42'")
row = c.fetchone()
print(f"\nID 42当前值: {row[1]} = {row[2]}")

conn.close()
