import sqlite3
conn = sqlite3.connect('C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db')
cursor = conn.cursor()

# Get table name as bytes
table_name = 'ģ�����ñ�'

# Get column info
cursor.execute("PRAGMA table_info(?)", (table_name,))
cols_info = cursor.fetchall()

# Get all data
cursor.execute("SELECT * FROM ?", (table_name,))
rows = cursor.fetchall()
columns = [description[0] for description in cursor.description]

print(f"Columns: {columns}")
print(f"Total rows: {len(rows)}")
