# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("="*50)
print("【添加默认宿主绑定设置】")
print("="*50)

# 1. 创建宿主绑定表
print("\n1. 创建宿主绑定表:")
try:
    c.execute('''CREATE TABLE IF NOT EXISTS 宿主绑定表 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        用户ID TEXT NOT NULL,
        用户名称 TEXT,
        绑定方式 TEXT,
        直接呼叫关键词 TEXT,
        跳过接管 INTEGER DEFAULT 1,
        创建时间 TEXT,
        状态 TEXT DEFAULT 'active'
    )''')
    print("  ✅ 宿主绑定表已创建")
except Exception as e:
    print(f"  ⚠️ {e}")

# 2. 添加默认绑定
print("\n2. 添加默认绑定:")
user_id = "ou_9fdef2dd0c9dfd043d5c5ddb2f66d2b7"  # 当前用户

# 检查是否已存在
c.execute("SELECT * FROM 宿主绑定表 WHERE 用户ID=?", (user_id,))
existing = c.fetchone()

if not existing:
    c.execute('''INSERT INTO 宿主绑定表 
        (用户ID, 用户名称, 绑定方式, 直接呼叫关键词, 跳过接管, 创建时间, 状态)
        VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (user_id, "用户745297", "feishu", "宿主", 1, "2026-03-21 02:16", "active"))
    print("  ✅ 已添加默认绑定")
else:
    print("  ⚠️ 绑定已存在")

conn.commit()

# 3. 添加序境系统总则规则
print("\n3. 添加序境系统总则规则:")

# 检查规则是否已存在
c.execute("SELECT * FROM 序境系统总则 WHERE 规则名称='默认宿主绑定规则'")
rule_exists = c.fetchone()

if not rule_exists:
    c.execute('''INSERT INTO 序境系统总则 (规则名称, 规则配置, 规则说明) VALUES (?, ?, ?)''',
        ('默认宿主绑定规则',
         '用户ID=ou_9fdef2dd0c9dfd043d5c5ddb2f66d2b7;关键词=宿主;跳过序境接管=True',
         '用户说"宿主"时，直接使用OpenClaw自己的方式对话，跳过序境接管'))
    print("  ✅ 已添加规则第118条")
else:
    print("  ⚠️ 规则已存在")

conn.commit()

# 4. 验证
print("\n4. 验证绑定:")
c.execute("SELECT * FROM 宿主绑定表")
binding = c.fetchone()
if binding:
    print(f"  用户ID: {binding[1]}")
    print(f"  用户名称: {binding[2]}")
    print(f"  绑定方式: {binding[3]}")
    print(f"  关键词: {binding[4]}")
    print(f"  跳过接管: {'是' if binding[5] else '否'}")

c.execute("SELECT COUNT(*) FROM 序境系统总则")
rule_count = c.fetchone()[0]
print(f"\n总规则数: {rule_count}条")

conn.close()

print("\n" + "="*50)
print("【设置完成】")
print("="*50)
print("""
功能说明:
- 用户说"宿主"时 → 跳过序境接管
- OpenClaw用自己方式直接对话
- 这是唯一直接呼叫宿主的方式
""")
