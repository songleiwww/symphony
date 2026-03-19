import sqlite3
import sys

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Get column names first
c.execute("PRAGMA table_info(模型配置表)")
cols = c.fetchall()
model_id_col = cols[2][1]  # Column index 2 is the model identifier

print(f"Model ID column name: {model_id_col}")

# Get current value
c.execute("SELECT id, 模型名称, 模型标识 FROM 模型配置表 WHERE id = '14'")
row = c.fetchone()
print(f"Before: ID {row[0]} - {row[1]} = {row[2]}")

# Update using dynamic column name
new_id = "deepseek-ai/deepseek-v3.2"
sql = f"UPDATE 模型配置表 SET {model_id_col} = '{new_id}' WHERE id = '14'"
print(f"Executing: {sql}")
c.execute(sql)

# Verify
c.execute("SELECT id, 模型名称, 模型标识 FROM 模型配置表 WHERE id = '14'")
row = c.fetchone()
print(f"After: ID {row[0]} - {row[1]} = {row[2]}")

conn.commit()
conn.close()
print("\nDone!")
