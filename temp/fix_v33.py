import sqlite3
import sys

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Get column names first
c.execute("PRAGMA table_info(模型配置表)")
cols = c.fetchall()
model_id_col = cols[2][1]  # Column index 2 is the model identifier
print(f"Model ID column name (raw): {repr(model_id_col)}")

# Get all rows to find ID 14
c.execute("SELECT * FROM 模型配置表")
all_rows = c.fetchall()

# Find ID 14
for row in all_rows:
    if row[0] == '14':
        print(f"Found ID 14: {row[1]} = {row[2]}")
        # Update using index
        new_id = "deepseek-ai/deepseek-v3.2"
        # Use positional update
        c.execute("UPDATE 模型配置表 SET 模型标识 = ? WHERE id = '14'", (new_id,))
        print(f"Updated to: {new_id}")
        break

conn.commit()

# Verify
c.execute("SELECT * FROM 模型配置表 WHERE id = '14'")
row = c.fetchone()
print(f"Verified: ID {row[0]} - {row[1]} = {row[2]}")

conn.close()
print("\nDone!")
