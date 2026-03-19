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

# Get all data with index
rows = c.execute(f"SELECT * FROM '{model_table}'").fetchall()

# Check enabled column (index 7)
print("Checking column 7 values:")
for row in rows[:3]:
    val = row[7]
    print(f"  repr: {repr(val)}")
    print(f"  bytes: {val.encode('utf-8')}")
    print(f"  == '启用': {val == '启用'}")
    print()

# Try using LIKE
print("\nUsing LIKE:")
rows_like = c.execute(f"SELECT id FROM '{model_table}' WHERE column7 LIKE '%启%'").fetchall()
print(f"  Found: {len(rows_like)}")

# Get total count
print(f"\nTotal models: {len(rows)}")
