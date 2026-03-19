import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# z-ai/glm5 doesn't exist, so update ID 15
new_model_id = "z-ai/glm5"

# Get current
c.execute("SELECT * FROM 模型配置表 WHERE id = '15'")
row = c.fetchone()
print(f"Before: ID {row[0]} - {row[1]} = {row[2]}")

# Update
c.execute("UPDATE 模型配置表 SET 模型标识符 = ? WHERE id = '15'", (new_model_id,))
print(f"After:  ID {row[0]} - {row[1]} = {new_model_id}")

conn.commit()
conn.close()
print("\nDone!")
