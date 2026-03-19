import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check if model exists
c.execute("SELECT * FROM 模型配置表 WHERE 模型标识符 = 'nvidia/nemotron-3-super-120b-a12b'")
rows = c.fetchall()

print("=== 搜索 nvidia/nemotron-3-super-120b-a12b ===")
if rows:
    for row in rows:
        print(f"ID {row[0]}: {row[1]} = {row[2]}")
else:
    print("未找到重复")
    
    # Replace ID 19
    c.execute("SELECT * FROM 模型配置表 WHERE id = '19'")
    row = c.fetchone()
    print(f"\n原 ID 19: {row[1]} = {row[2]}")
    
    new_id = "nvidia/nemotron-3-super-120b-a12b"
    c.execute("UPDATE 模型配置表 SET 模型标识符 = ? WHERE id = '19'", (new_id,))
    print(f"新 ID 19: NV Embed v2 = {new_id}")

conn.commit()
conn.close()
print("\nDone!")
