import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Use the correct column name: 模型标识符
new_id = "deepseek-ai/deepseek-v3.2"

# Get current value first
c.execute("SELECT * FROM 模型配置表 WHERE id = '14'")
row = c.fetchone()
print(f"Before: ID {row[0]} - {row[1]} = {row[2]}")

# Update using correct column name
c.execute("UPDATE 模型配置表 SET 模型标识符 = ? WHERE id = '14'", (new_id,))
print(f"Updated to: {new_id}")

conn.commit()

# Verify
c.execute("SELECT * FROM 模型配置表 WHERE id = '14'")
row = c.fetchone()
print(f"After: ID {row[0]} - {row[1]} = {row[2]}")

conn.close()
print("\nDone!")
