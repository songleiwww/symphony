import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check if qwen3-coder-480b exists
c.execute("SELECT * FROM 模型配置表 WHERE 模型标识符 LIKE '%qwen3-coder%'")
rows = c.fetchall()

print("=== 搜索 qwen3-coder-480b ===")
if rows:
    for row in rows:
        print(f"ID {row[0]}: {row[1]} = {row[2]}")
else:
    print("未找到重复，将替换 ID 8")

# Get ID 8 current value
c.execute("SELECT * FROM 模型配置表 WHERE id = '8'")
row = c.fetchone()
print(f"\nID 8当前值: {row[1]} = {row[2]}")

if not rows:
    # Replace
    new_id = "qwen/qwen3-coder-480b-a35b-instruct"
    c.execute("UPDATE 模型配置表 SET 模型标识符 = ? WHERE id = '8'", (new_id,))
    print(f"已更新为: {new_id}")

conn.commit()
conn.close()
print("\nDone!")
