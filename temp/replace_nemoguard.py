import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check if nvidia/llama-3.1-nemoguard-8b-content-safety exists
c.execute("SELECT * FROM 模型配置表 WHERE 模型标识符 = 'nvidia/llama-3.1-nemoguard-8b-content-safety'")
rows = c.fetchall()

print("=== 搜索 nvidia/llama-3.1-nemoguard-8b-content-safety ===")
if rows:
    for row in rows:
        print(f"ID {row[0]}: {row[1]} = {row[2]}")
    print("\n✅ 模型已存在，无需替换")
else:
    print("未找到，将替换一个无效模型")
    # Find an invalid model - let's try ESMFold (ID 25)
    c.execute("SELECT * FROM 模型配置表 WHERE id = '25'")
    row = c.fetchone()
    print(f"\n将替换 ID 25: {row[1]}")
    
    new_id = "nvidia/llama-3.1-nemoguard-8b-content-safety"
    c.execute("UPDATE 模型配置表 SET 模型标识符 = ? WHERE id = '25'", (new_id,))
    print(f"已更新为: {new_id}")

conn.commit()
conn.close()
print("\nDone!")
