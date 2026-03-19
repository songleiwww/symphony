import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Update Qwen2 models based on user's validation
# ID 53 is confirmed valid: qwen/qwen2-7b-instruct
# For ID 51 and 52, they should be different sizes

updates = [
    ('53', 'qwen/qwen2-7b-instruct'),  # Qwen2 7B - confirmed valid
    ('51', 'qwen/qwen2-0.5b-instruct'),  # Qwen2 0.5B
    ('52', 'qwen/qwen2-1.5b-instruct'),  # Qwen2 1.5B
]

for mid, new_id in updates:
    c.execute(f"SELECT * FROM 模型配置表 WHERE id = '{mid}'")
    row = c.fetchone()
    print(f"Before: ID {row[0]} - {row[1]} = {row[2]}")
    
    c.execute(f"UPDATE 模型配置表 SET 模型标识符 = '{new_id}' WHERE id = '{mid}'")
    print(f"After:  ID {row[0]} - {row[1]} = {new_id}\n")

conn.commit()
conn.close()
print("Done!")
