# -*- coding: utf-8 -*-
"""
序境系统 - 修改前自动备份机制
"""
import sqlite3
import os
import shutil
from datetime import datetime
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'

def auto_backup(tables=['模型配置表', '官署角色表', '序境系统总则']):
    """修改前自动备份关键表"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    backup_count = 0
    for table in tables:
        try:
            # 检查表是否存在
            c.execute(f"SELECT name FROM sqlite_master WHERE name='{table}'")
            if not c.fetchone():
                continue
                
            # 创建备份表
            backup_table = f"_{table}_auto_{timestamp}"
            c.execute(f"CREATE TABLE IF NOT EXISTS {backup_table} AS SELECT * FROM {table}")
            backup_count += 1
            print(f"  ✅ 备份: {table} → {backup_table}")
        except Exception as e:
            print(f"  ❌ 备份失败: {table} - {e}")
    
    # 清理旧的自动备份（保留最近3个）
    try:
        old_backups = [t for t in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '_{table}_auto_%'".format(table=tables[0])).fetchall()]
        if len(old_backups) > 3:
            for old in old_backups[:-3]:
                c.execute(f"DROP TABLE IF EXISTS {old}")
                print(f"  🗑️ 清理: {old}")
    except:
        pass
    
    conn.commit()
    conn.close()
    return backup_count

print("="*60)
print("【自动备份测试】")
print("="*60)
count = auto_backup(['模型配置表', '官署角色表', '序境系统总则'])
print(f"\n已备份 {count} 个表")

# 验证
conn = sqlite3.connect(db_path)
c = conn.cursor()
auto_tables = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_auto_%'").fetchall()
print(f"\n现有自动备份: {len(auto_tables)}个")
for t in auto_tables[-5:]:
    print(f"  - {t[0]}")
conn.close()
