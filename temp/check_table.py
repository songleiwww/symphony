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

print(f"Model table: {model_table}")

if model_table:
    # Get columns
    cols = c.execute(f"PRAGMA table_info('{model_table}')").fetchall()
    print("\nColumns:")
    for col in cols:
        print(f"  {col[1]}: {col[2]}")
    
    # Get data
    rows = c.execute(f"SELECT * FROM '{model_table}'").fetchall()
    print(f"\nTotal rows: {len(rows)}")
    
    # Show first 5
    print("\nFirst 5 rows:")
    for row in rows[:5]:
        print(row)
