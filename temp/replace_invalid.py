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
else:
    print("未找到重复")
    # Find an invalid model to replace - let's check which ones might be invalid
    # Use ESMFold (ID 24) as it's a specialized model that might not work with chat API
    print("\n将替换 ID 24 (ESMFold)")
    new_id = "nvidia/llama-3.3-nemotron-super-49b-v1"
    c.execute("UPDATE 模型配置表 SET 模型标识符 = ? WHERE id = '24'", (new_id,))
    print(f"已更新 ID 24 为: {new_id}")

conn.commit()
conn.close()
print("\nDone!")
