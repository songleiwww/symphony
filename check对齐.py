# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 检查模型配置表数量
c.execute("SELECT COUNT(*) FROM 模型配置表")
model_count = c.fetchone()[0]
print(f"模型配置表: {model_count}个")

# 检查官署角色表数量
c.execute("SELECT COUNT(*) FROM 官署角色表")
role_count = c.fetchone()[0]
print(f"官署角色表: {role_count}个")

# 检查官署分布
c.execute("SELECT 所属官署, COUNT(*) as cnt FROM 官署角色表 GROUP BY 所属官署")
print("\n官署分布:")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]}个")

# 找出多余的1个角色
if role_count > model_count:
    diff = role_count - model_count
    print(f"\n官署角色表多了{diff}个，需要删除")
    # 查看最后添加的角色
    c.execute("SELECT id, 姓名, 模型配置表_ID FROM 官署角色表 ORDER BY id DESC LIMIT 5")
    print("最后5个角色:")
    for row in c.fetchall():
        print(f"  {row}")
