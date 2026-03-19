import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check current value of ID 6
c.execute("SELECT * FROM 模型配置表 WHERE id = '6'")
row = c.fetchone()
print(f"ID 6当前值: {row[1]} = {row[2]}")

# The user confirmed nvidia/llama-3.3-nemotron-super-49b-v1 is valid
# It appears to already be the same, let's confirm
current_id = row[2]
new_id = "nvidia/llama-3.3-nemotron-super-49b-v1"

if current_id == new_id:
    print(f"\n✅ ID 6 已经是正确的: {new_id}")
else:
    c.execute("UPDATE 模型配置表 SET 模型标识符 = ? WHERE id = '6'", (new_id,))
    print(f"\n已更新 ID 6 为: {new_id}")

conn.commit()
conn.close()
print("\nDone!")
