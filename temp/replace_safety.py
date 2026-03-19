import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check if model exists
c.execute("SELECT * FROM 模型配置表 WHERE 模型标识符 = 'nvidia/llama-3.1-nemotron-safety-guard-8b-v3'")
rows = c.fetchall()

print("=== 搜索 nvidia/llama-3.1-nemotron-safety-guard-8b-v3 ===")
if rows:
    for row in rows:
        print(f"ID {row[0]}: {row[1]} = {row[2]}")
else:
    print("未找到重复，将替换 ID 18")
    # Replace ID 18
    c.execute("SELECT * FROM 模型配置表 WHERE id = '18'")
    row = c.fetchone()
    print(f"\n原 ID 18: {row[1]} = {row[2]}")
    
    new_id = "nvidia/llama-3.1-nemotron-safety-guard-8b-v3"
    c.execute("UPDATE 模型配置表 SET 模型标识符 = ? WHERE id = '18'", (new_id,))
    print(f"新 ID 18: NV Embed v1 = {new_id}")

conn.commit()
conn.close()
print("\nDone!")
