import sqlite3

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
c = conn.cursor()

# Find the model config table
tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
model_table = None
for t in tables:
    if '模型' in t and '配置' in t:
        model_table = t
        break

# Use index-based update
correct_model_id = "deepseek-ai/deepseek-r1-distill-qwen-32b"

# Get current value first
c.execute(f"SELECT * FROM '{model_table}' WHERE id = '12'")
row = c.fetchone()
print(f"Before: ID 12 = {row[2]}")

# Update using index 2 (model identifier column)
c.execute(f"UPDATE '{model_table}' SET 模型标识 = ? WHERE id = '12'", (correct_model_id,))
print(f"After: ID 12 = {correct_model_id}")

conn.commit()
conn.close()
print("\nDone!")
