import sqlite3

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

# Find the model config table - it's the one with most columns about models
model_table = None
for t in tables:
    table_name = t[0]
    cursor.execute(f"PRAGMA table_info('{table_name}')")
    cols = [c[1] for c in cursor.fetchall()]
    # Check if this looks like a model config table
    col_str = str(cols)
    if '模型' in col_str and ('名称' in col_str or '服务商' in col_str or 'API' in col_str):
        model_table = table_name
        print(f"Found model table: {table_name}")
        print(f"Columns: {cols}")
        break

if not model_table:
    # Fallback: find table with most rows that has model-related columns
    print("Searching for model table...")
    for t in tables:
        table_name = t[0]
        cursor.execute(f"SELECT COUNT(*) FROM '{table_name}'")
        count = cursor.fetchone()[0]
        cursor.execute(f"PRAGMA table_info('{table_name}')")
        cols = [c[1] for c in cursor.fetchall()]
        col_str = str(cols)
        if count > 10 and ('模型' in col_str or 'model' in col_str.lower()):
            print(f"  {table_name}: {count} rows, cols: {cols[:8]}")

conn.close()
