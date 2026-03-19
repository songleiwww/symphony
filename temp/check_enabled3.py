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

# Get column names
cursor = c.execute(f"SELECT * FROM '{model_table}' LIMIT 1")
columns = [d[0] for d in cursor.description]

print("Columns (raw):")
for i, col in enumerate(columns):
    print(f"  {i}: {repr(col)}")

# Find enabled column (index 7 based on earlier output)
print("\n\nChecking enabled status (column 7):")
enabled_values = set()
for row in rows[:10]:
    enabled = row[7]
    enabled_values.add(enabled)
    print(f"  ID {row[0]}: [{enabled}]")

print(f"\nUnique values in column 7: {enabled_values}")

# Now check using that value
print("\n\n=== Checking all enabled models ===")
count = 0
for row in rows:
    if row[7] == '启用':
        count += 1
        
print(f"Models with '启用': {count}")
