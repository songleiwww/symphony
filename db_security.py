# -*- coding: utf-8 -*-
import sqlite3
import os
import shutil
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'

print("="*60)
print("【数据库文件安全指南】")
print("="*60)

# 检查表
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()

print("\n📁 当前数据库:")
print(f"  路径: {db_path}")
print(f"  大小: {os.path.getsize(db_path) / 1024:.1f} KB")
print(f"  表数量: {len(tables)}")

print("\n📋 数据表:")
for t in tables:
    c.execute(f"SELECT COUNT(*) FROM {t[0]}")
    count = c.fetchone()[0]
    print(f"  - {t[0]}: {count}条")

conn.close()

print("\n" + "="*60)
print("【安全策略】")
print("="*60)

# 检查是否有备份
backup_dir = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/'
backups = [f for f in os.listdir(backup_dir) if 'backup' in f.lower() or f.endswith('.db')]
print(f"\n📦 现有备份: {len(backups)}个")
for b in backups[:5]:
    print(f"  - {b}")

print("\n" + "="*60)
print("【恢复方法】")
print("="*60)

print("""
🔧 失误挽救方法：

1. 【自动备份】
   - SQLite会自动创建 .db-journal 文件
   - 记录最近的事务操作

2. 【手动备份】
   复制文件:
   copy symphony.db symphony_backup_20260321.db

3. 【恢复步骤】
   - 停止程序
   - 复制备份覆盖原文件
   - 重启程序

4. 【误删恢复】
   - 从回收站恢复
   - 使用文件恢复工具

5. 【事务回滚】
   - 如果刚删除数据，立即:
   .restore symphony.db
""")

print("\n" + "="*60)
print("【建议】")
print("="*60)
print("""
✅ 每次重大操作前手动备份
✅ 定期自动备份（如每天）
✅ 重要数据导出为SQL文件
✅ 保留3个以上备份版本
""")
