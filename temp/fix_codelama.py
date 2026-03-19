import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Fix Code Llama models
fixes = [
    ('17', 'meta/codellama-34b-instruct'),  # Code Llama 34B
    ('16', 'meta/codellama-70b-instruct'),   # Code Llama 70B
]

print("=== 修复英伟达模型 ===\n")

for model_id, new_model_id in fixes:
    # Get current
    c.execute(f"SELECT * FROM 模型配置表 WHERE id = '{model_id}'")
    row = c.fetchone()
    print(f"Before: ID {row[0]} - {row[1]} = {row[2]}")
    
    # Update
    c.execute(f"UPDATE 模型配置表 SET 模型标识符 = '{new_model_id}' WHERE id = '{model_id}'")
    print(f"After:  ID {row[0]} - {row[1]} = {new_model_id}\n")

conn.commit()
conn.close()
print("Done!")
