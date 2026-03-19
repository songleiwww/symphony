# -*- coding: utf-8 -*-
import sqlite3
conn = sqlite3.connect('C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db')
c = conn.cursor()

# Update DeepSeek R1 Distill 70B (ID 14) with correct model ID
new_model_id = "deepseek-ai/deepseek-v3.2"

# Show current value
c.execute("SELECT * FROM 模型配置表 WHERE id = '14'")
row = c.fetchone()
print(f"Before: ID 14 = {row[2]}")

# Update
c.execute("UPDATE 模型配置表 SET 模型标识 = ? WHERE id = '14'", (new_model_id,))
print(f"After: ID 14 = {new_model_id}")

c.commit()
conn.close()
print("\nDone!")
