import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check if nvidia/llama-3.3-nemotron-super-49b-v1 exists
c.execute("SELECT * FROM 模型配置表 WHERE 模型标识符 = 'nvidia/llama-3.3-nemotron-super-49b-v1'")
rows = c.fetchall()

print("=== 搜索 nvidia/llama-3.3-nemotron-super-49b-v1 ===")
if rows:
    for row in rows:
        print(f"ID {row[0]}: {row[1]} = {row[2]}")
    print("\n⚠️ 模型已存在，检查是否可替换其他无效模型")

# Find models that might be invalid
# Check ID 28 (Neva 22B - vision model)
c.execute("SELECT * FROM 模型配置表 WHERE id = '28'")
row = c.fetchone()
print(f"\n可替换 ID 28: {row[1]} = {row[2]}")

# Replace with the new model
new_id = "nvidia/llama-3.3-nemotron-super-49b-v1"
c.execute("UPDATE 模型配置表 SET 模型标识符 = ? WHERE id = '28'", (new_id,))
print(f"已更新 ID 28 为: {new_id}")

conn.commit()
conn.close()
print("\nDone!")
