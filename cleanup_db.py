# -*- coding: utf-8 -*-
"""
序境系统 - 数据库整理执行
"""
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("="*60)
print("【数据库整理执行】")
print("="*60)

# 1. 删除空表
print("\n🗑️ 删除空表:")
empty_tables = ['Token使用日志表']
for t in empty_tables:
    try:
        c.execute(f"DROP TABLE IF EXISTS {t}")
        print(f"  ✅ 删除: {t}")
    except Exception as e:
        print(f"  ❌ 失败: {t} - {e}")

# 2. 清理旧备份表（保留最新3个）
print("\n📦 清理旧备份表:")

# 获取所有模型配置表备份
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_模型配置表_%'")
model_backups = [r[0] for r in c.fetchall()]

# 保留最新的2个
keep_count = 2
if len(model_backups) > keep_count:
    # 按时间排序（假设名字包含日期）
    model_backups.sort()
    for old in model_backups[:-keep_count]:
        try:
            c.execute(f"DROP TABLE IF EXISTS {old}")
            print(f"  ✅ 删除: {old}")
        except Exception as e:
            print(f"  ❌ 失败: {old}")

# 3. 清理官署角色表旧备份
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_官署角色表_%'")
role_backups = [r[0] for r in c.fetchall()]
if len(role_backups) > keep_count:
    role_backups.sort()
    for old in role_backups[:-keep_count]:
        try:
            c.execute(f"DROP TABLE IF EXISTS {old}")
            print(f"  ✅ 删除: {old}")
        except Exception as e:
            print(f"  ❌ 失败: {old}")

# 4. 清理序境系统总则旧备份
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_序境系统总则_%'")
rule_backups = [r[0] for r in c.fetchall()]
if len(rule_backups) > keep_count:
    rule_backups.sort()
    for old in rule_backups[:-keep_count]:
        try:
            c.execute(f"DROP TABLE IF EXISTS {old}")
            print(f"  ✅ 删除: {old}")
        except Exception as e:
            print(f"  ❌ 失败: {old}")

conn.commit()

# 验证
print("\n" + "="*60)
print("【整理后】")
print("="*60)
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
print(f"总表数: {len(tables)}")

for t in tables:
    c.execute(f"SELECT COUNT(*) FROM {t[0]}")
    count = c.fetchone()[0]
    print(f"  {t[0]}: {count}")

conn.close()
print("\n✅ 整理完成")
