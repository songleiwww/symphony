import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check if exact model exists
c.execute("SELECT * FROM 模型配置表 WHERE 模型标识符 = 'minimaxai/minimax-m2.1'")
rows = c.fetchall()

print("=== 搜索 minimax-m2.1 ===")
if rows:
    for row in rows:
        print(f"ID {row[0]}: {row[1]} = {row[2]}")
    print("\n⚠️ 模型已存在")
else:
    print("未找到完全相同的模型")
    
    # Replace ID 28 (currently has v1, but user wants to use minimax-m2.1)
    c.execute("SELECT * FROM 模型配置表 WHERE id = '28'")
    row = c.fetchone()
    print(f"\n将替换 ID 28: {row[1]} = {row[2]}")
    
    new_id = "minimaxai/minimax-m2.1"
    c.execute("UPDATE 模型配置表 SET 模型标识符 = ? WHERE id = '28'", (new_id,))
    print(f"已更新 ID 28 为: {new_id}")

conn.commit()
conn.close()
print("\nDone!")
