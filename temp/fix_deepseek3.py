import sqlite3

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Get table info
c.execute("PRAGMA table_info('模型配置表')")
cols = c.fetchall()
print("Columns:")
for col in cols:
    print(f"  {col[1]}")

# Update ID 12 - use the column name as-is from the table
c.execute("UPDATE 模型配置表 SET 模型标识 = 'deepseek-ai/deepseek-r1-distill-qwen-32b' WHERE id = '12'")
print(f"\nUpdated {c.rowcount} row(s)")

conn.commit()

# Verify
c.execute("SELECT id, 模型名称, 模型标识 FROM 模型配置表 WHERE id = '12'")
row = c.fetchone()
print(f"Verified: ID {row[0]} - {row[1]} = {row[2]}")

conn.close()
print("\nDone!")
