import sqlite3
c = sqlite3.connect('C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db')
c.text_factory = str

# Find the model config table
tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
model_table = None
for t in tables:
    if '模型' in t and '配置' in t:
        model_table = t
        break

# Get enabled column values
rows = c.execute(f"SELECT id, 模型名称, 是否启用 FROM '{model_table}'").fetchall()

print("Enabled column values:")
enabled_values = set()
for row in rows:
    enabled_values.add(row[2])
    print(f"  ID {row[0]}: {row[1][:20]} -> [{row[2]}]")

print(f"\nUnique enabled values: {enabled_values}")
