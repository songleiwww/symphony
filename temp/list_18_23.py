import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Get IDs 18-23
c.execute("""
    SELECT id, 模型名称, 模型标识符 
    FROM 模型配置表 
    WHERE id BETWEEN 18 AND 23
    ORDER BY id
""")
rows = c.fetchall()

print("=== ID 18-23 详细信息 ===\n")
for row in rows:
    print(f"ID {row[0]}: {row[1]}")
    print(f"    模型ID: {row[2]}\n")

conn.close()
