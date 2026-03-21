# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("="*50)
print("【添加对话反馈规则】")
print("="*50)

# 添加新规则
c.execute('''INSERT INTO 序境系统总则 (规则名称, 规则配置, 规则说明) VALUES (?, ?, ?)''',
    ('对话反馈规则', 
     'token统计=True;显示模型=True;显示服务商=True;显示绑定人=True',
     '对话响应必须包含：1)Tokens消耗数量 2)使用的模型名称 3)服务商 4)绑定的人/角色'))

conn.commit()

# 验证
c.execute("SELECT * FROM 序境系统总则 WHERE 规则名称='对话反馈规则'")
result = c.fetchone()

if result:
    print(f"✅ 已添加规则 ID: {result[0]}")
    print(f"   规则名称: {result[1]}")
    print(f"   规则配置: {result[2]}")
    print(f"   规则说明: {result[3]}")
else:
    print("❌ 添加失败")

# 统计总数
c.execute("SELECT COUNT(*) FROM 序境系统总则")
count = c.fetchone()[0]
print(f"\n总规则数: {count}条")

conn.close()
