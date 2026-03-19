import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Get all NVIDIA models with issues (ID 7, 9, 10, 15, 16, 17)
problem_ids = ['7', '9', '10', '15', '16', '17']

print("=== 英伟达问题模型 ===\n")

for pid in problem_ids:
    c.execute(f"SELECT * FROM 模型配置表 WHERE id = '{pid}'")
    row = c.fetchone()
    if row:
        print(f"ID {row[0]}: {row[1]} = {row[2]}")

conn.close()
