# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("="*50)
print("【添加关键词：步花间】")
print("="*50)

# 添加关键词
c.execute("UPDATE 宿主绑定表 SET 直接呼叫关键词=? WHERE 用户ID=?",
          ("宿主,步花间", "ou_9fdef2dd0c9dfd043d5c5ddb2f66d2b7"))

# 更新规则
c.execute("UPDATE 序境系统总则 SET 规则配置=? WHERE 规则名称=?",
          ("用户ID=ou_9fdef2dd0c9dfd043d5c5ddb2f66d2b7;关键词=宿主,步花间;跳过序境接管=True",
           "默认宿主绑定规则"))

conn.commit()

# 验证
c.execute("SELECT 直接呼叫关键词 FROM 宿主绑定表 WHERE 用户ID=?", 
          ("ou_9fdef2dd0c9dfd043d5c5ddb2f66d2b7",))
kw = c.fetchone()
print(f"\n关键词已更新: {kw[0]}")

conn.close()

print("\n✅ 设置完成")
print("""
功能说明:
- 用户说"宿主"或"步花间"时 → 跳过序境接管
- OpenClaw用自己方式直接对话
""")
