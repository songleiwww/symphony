# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("="*50)
print("【设置宿主页名称】")
print("="*50)

# 添加宿主页名称
c.execute("UPDATE 宿主绑定表 SET 用户名称=? WHERE 用户ID=?",
          ("步花间", "ou_9fdef2dd0c9dfd043d5c5ddb2f66d2b7"))

conn.commit()

# 验证
c.execute("SELECT 用户名称, 直接呼叫关键词 FROM 宿主绑定表 WHERE 用户ID=?", 
          ("ou_9fdef2dd0c9dfd043d5c5ddb2f66d2b7",))
result = c.fetchone()

print(f"宿主页名称: {result[0]}")
print(f"关键词: {result[1]}")

conn.close()

print("\n✅ 设置完成")
