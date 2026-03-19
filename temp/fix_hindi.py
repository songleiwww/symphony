import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Update ID 10 with new model ID from user
new_model_id = "nvidia/gliner-pii"

# Get current
c.execute("SELECT * FROM 模型配置表 WHERE id = '10'")
row = c.fetchone()
print(f"Before: ID {row[0]} - {row[1]} = {row[2]}")

# Update
c.execute("UPDATE 模型配置表 SET 模型标识符 = ? WHERE id = '10'", (new_model_id,))
print(f"After:  ID {row[0]} - {row[1]} = {new_model_id}")

conn.commit()
conn.close()
print("\nDone!")
