# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("="*50)
print("【添加会话尾标规则】")
print("="*50)

# 添加规则
c.execute('''INSERT INTO 序境系统总则 (规则名称, 规则配置, 规则说明) VALUES (?, ?, ?)''',
    ('会话尾标规则', 
     '尾标格式=【陆念昭】;必须显示=True;位置=会话尾部',
     'OpenClaw和序境系统会话尾部必须显示智能体尾标，如【陆念昭】'))

conn.commit()

# 验证
c.execute("SELECT * FROM 序境系统总则 WHERE 规则名称='会话尾标规则'")
result = c.fetchone()

if result:
    print(f"✅ 已添加规则 ID: {result[0]}")
    print(f"   规则名称: {result[1]}")
    print(f"   规则配置: {result[2]}")
    print(f"   规则说明: {result[3]}")

c.execute("SELECT COUNT(*) FROM 序境系统总则")
count = c.fetchone()[0]
print(f"\n总规则数: {count}条")

conn.close()

print("\n" + "="*50)
print("【设置完成】")
print("="*50)
print("""
会话示例:
用户: 你好
序境: 你好呀～【陆念昭】

或

用户: 宿主你好
OpenClaw: 你好～【宿主】
""")
