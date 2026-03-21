# -*- coding: utf-8 -*-
"""
序境系统 - 数据库整理
"""
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("="*60)
print("【数据库整理分析】")
print("="*60)

# 1. 获取所有表
c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
all_tables = [r[0] for r in c.fetchall()]

print(f"\n总表数: {len(all_tables)}")

# 2. 分析每个表
table_info = []
for table in all_tables:
    c.execute(f"SELECT COUNT(*) FROM {table}")
    count = c.fetchone()[0]
    
    # 检查是否是临时/备份表
    is_temp = any(x in table.lower() for x in ['_old_', '_backup', '_auto_', '_temp', 'sqlite_'])
    
    table_info.append({
        'name': table,
        'count': count,
        'is_temp': is_temp
    })

# 3. 分类
print("\n【表分类】")
print("-"*60)

# 核心表（保留）
core_tables = ['模型配置表', '官署角色表', '序境系统总则', '官署表', '调度规则表']
print("\n✅ 核心表:")
for t in table_info:
    if t['name'] in core_tables:
        print(f"  {t['name']}: {t['count']}条")

# 备份表（可清理旧的）
backup_tables = [t for t in table_info if t['is_temp']]
print(f"\n📦 备份/临时表 ({len(backup_tables)}个):")
for t in backup_tables:
    print(f"  {t['name']}: {t['count']}条")

# 空表（可删除）
empty_tables = [t for t in table_info if t['count'] == 0 and not t['is_temp']]
print(f"\n🗑️ 空表 ({len(empty_tables)}个):")
for t in empty_tables:
    print(f"  {t['name']}")

# 其他表
other_tables = [t for t in table_info if not t['is_temp'] and t['count'] > 0 and t['name'] not in core_tables]
print(f"\n📋 其他表 ({len(other_tables)}个):")
for t in other_tables:
    print(f"  {t['name']}: {t['count']}条")

conn.close()

print("\n" + "="*60)
print("【整理建议】")
print("="*60)

print("""
1. 备份表: 保留最新的3个，其余删除
2. 空表: 可删除
3. 孤立表: 检查关联后删除
4. 规则统一: 所有规则存入序境系统总则表
""")
