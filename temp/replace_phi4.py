import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check if microsoft/phi-4-mini-flash-reasoning exists
c.execute("SELECT * FROM 模型配置表 WHERE 模型标识符 LIKE '%phi-4-mini%'")
rows = c.fetchall()

print("=== 搜索 phi-4-mini ===")
if rows:
    for row in rows:
        print(f"ID {row[0]}: {row[1]} = {row[2]}")
else:
    print("未找到重复，将替换 nvidia/llama-3.1-nemoguard-8b-content-safety")
    
    # Find a model to replace - check ID 11 first
    c.execute("SELECT * FROM 模型配置表 WHERE id = '11'")
    row = c.fetchone()
    print(f"\nID 11当前值: {row[1]} = {row[2]}")
    
    new_id = "microsoft/phi-4-mini-flash-reasoning"
    c.execute("UPDATE 模型配置表 SET 模型标识符 = ? WHERE id = '11'", (new_id,))
    print(f"已更新 ID 11 为: {new_id}")

conn.commit()
conn.close()
print("\nDone!")
