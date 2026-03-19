import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check current value of ID 11
c.execute("SELECT * FROM 模型配置表 WHERE id = '11'")
row = c.fetchone()
print(f"Before: ID {row[0]} - {row[1]} = {row[2]}")

# Update with the new model ID
new_id = "nvidia/llama-3.1-nemoguard-8b-content-safety"
c.execute("UPDATE 模型配置表 SET 模型标识符 = ? WHERE id = '11'", (new_id,))
print(f"After:  ID {row[0]} - {row[1]} = {new_id}")

conn.commit()
conn.close()
print("\nDone!")
