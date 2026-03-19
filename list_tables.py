import sqlite3

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cursor = conn.cursor()

# Get all tables with their schema
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("All tables:")
for t in tables:
    table_name = t[0]
    cursor.execute(f"PRAGMA table_info('{table_name}')")
    cols = [c[1] for c in cursor.fetchall()]
    print(f"  {table_name}: {cols[:5]}...")  # Show first 5 columns

conn.close()
