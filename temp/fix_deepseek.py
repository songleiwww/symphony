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

# Get all columns
c.execute(f"SELECT * FROM '{model_table}' LIMIT 1")
columns = [desc[0] for desc in c.description]
print(f"Columns: {columns}")

# Find column indices
IDX_ID = 0
IDX_NAME = 1
IDX_MODEL_ID = 2

# Find DeepSeek R1 models
c.execute(f"SELECT * FROM '{model_table}'")
all_rows = c.fetchall()
deepseek_rows = [r for r in all_rows if 'DeepSeek' in str(r[IDX_NAME])]

print("\n=== DeepSeek模型 ===")
for row in deepseek_rows:
    print(f"ID {row[IDX_ID]}: {row[IDX_NAME]} - {row[IDX_MODEL_ID]}")

# Update ID 12 (DeepSeek R1) - using exact model ID from user
correct_model_id = "deepseek-ai/deepseek-r1-distill-qwen-32b"
c.execute(f"UPDATE '{model_table}' SET 模型标识 = ? WHERE id = '12'", (correct_model_id,))
print(f"\n已更新 ID 12 为: {correct_model_id}")

conn.commit()
conn.close()
print("\nDone!")
