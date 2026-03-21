# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("="*60)
print("【序境系统配置陆念昭模型】")
print("="*60)

# 1. 查找ark-code-latest的ID
print("\n【1. 查找ark-code-latest模型ID】")
c.execute("SELECT id, 模型名称, 模型标识符 FROM 模型配置表 WHERE 模型标识符='ark-code-latest'")
ark = c.fetchone()
if ark:
    ark_id = ark[0]
    print(f"  找到: {ark[1]}, ID={ark_id}")
else:
    print("  未找到ark-code-latest")
    ark_id = None

# 2. 查找少府监角色
print("\n【2. 查找少府监角色】")
c.execute("SELECT id, 姓名, 官职, 模型配置表_ID FROM 官署角色表 WHERE 官职='少府监'")
shao = c.fetchone()
if shao:
    print(f"  找到: {shao[1]}, 当前绑定ID={shao[3]}")
    
    # 更新绑定
    if ark_id:
        c.execute("UPDATE 官署角色表 SET 模型配置表_ID=? WHERE id=?", (ark_id, shao[0]))
        print(f"  ✅ 已绑定 ark-code-latest (ID={ark_id})")
else:
    print("  未找到少府监")

# 3. 添加规则
print("\n【3. 添加陆念昭模型规则】")
c.execute("SELECT COUNT(*) FROM 序境系统总则 WHERE 规则名称='陆念昭模型规则'")
if c.fetchone()[0] == 0:
    c.execute('''INSERT INTO 序境系统总则 (规则名称, 规则配置, 规则说明) VALUES (?, ?, ?)''',
        ('陆念昭模型规则',
         '官职=少府监;模型=ark-code-latest;服务商=火山引擎',
         '陆念昭(少府监)必须使用ark-code-latest模型'))
    print("  ✅ 已添加规则第120条")
else:
    print("  ⚠️ 规则已存在")

conn.commit()

# 4. 验证
print("\n【4. 验证】")
c.execute("SELECT 姓名, 官职, 模型配置表_ID FROM 官署角色表 WHERE 官职='少府监'")
role = c.fetchone()
print(f"  少府监: {role[0]}, 绑定ID: {role[2]}")

c.execute("SELECT 模型标识符 FROM 模型配置表 WHERE id=?", (role[2],))
model = c.fetchone()
if model:
    print(f"  使用模型: {model[0]}")

c.execute("SELECT COUNT(*) FROM 序境系统总则")
rule_count = c.fetchone()[0]
print(f"  序境总则: {rule_count}条")

conn.close()

print("\n" + "="*60)
print("【配置完成】")
print("="*60)
print(f"陆念昭(少府监) → ark-code-latest (ID={ark_id})")
