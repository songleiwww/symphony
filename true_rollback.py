# -*- coding: utf-8 -*-
"""
序境系统 - 真正的回滚实现
"""
import sqlite3
import shutil
import os
from datetime import datetime

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db"
BACKUP_DIR = "C:/Users/Administrator/.openclaw/workspace/skills/symphony/backups/"

def true_rollback(feature_name, backup_path):
    """
    真正的回滚：从备份文件恢复到原位置
    """
    print("="*50)
    print(f"【执行回滚: {feature_name}】")
    print("="*50)
    
    if not os.path.exists(backup_path):
        print(f"❌ 备份文件不存在: {backup_path}")
        return False
    
    # 读取备份内容
    with open(backup_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 确定目标路径
    filename = os.path.basename(backup_path).split('_')[0]
    # 从备份名推断原文件名
    name_map = {
        'memory_loader': 'memory_loader.py',
        'auto_test': 'auto_test.py', 
        'gray_rollback': 'gray_rollback.py',
        'safe_cleanup': 'safe_cleanup.py',
        'data_schema_snapshot': 'data/schema_snapshot.json',
        'data_core_features': 'data/core_features.json'
    }
    
    target_name = name_map.get(filename.split('_')[0], filename)
    target_path = "C:/Users/Administrator/.openclaw/workspace/skills/symphony/" + target_name
    
    # 先备份当前版本（防丢失）
    if os.path.exists(target_path):
        current_backup = target_path + '.pre_rollback'
        shutil.copy2(target_path, current_backup)
        print(f"  ✅ 当前版本已备份: {current_backup}")
    
    # 恢复备份
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✅ 已恢复: {target_path}")
    
    # 更新数据库状态
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE 功能备份表 SET 状态='已回滚', 备份时间=? WHERE 备份路径=?", 
              (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), backup_path))
    conn.commit()
    conn.close()
    
    print("="*50)
    print("【回滚完成】")
    print("="*50)
    return True

def list_backups():
    """列出所有可用备份"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 功能名称, 备份版本, 备份时间, 状态, 备份路径 FROM 功能备份表 ORDER BY id DESC")
    backups = c.fetchall()
    conn.close()
    
    print("\n" + "="*50)
    print("【可用备份列表】")
    print("="*50)
    for b in backups:
        print(f"功能: {b[0]}")
        print(f"  版本: {b[1]}")
        print(f"  时间: {b[2]}")
        print(f"  状态: {b[3]}")
        print(f"  路径: {b[4]}")
        print("-"*30)
    
    return backups

def emergency_restore():
    """紧急恢复：恢复到最新可用备份"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 功能名称, 备份路径 FROM 功能备份表 WHERE 状态='active' ORDER BY id DESC LIMIT 6")
    backups = c.fetchall()
    conn.close()
    
    print("\n" + "="*50)
    print("【紧急恢复】")
    print("="*50)
    
    for feature, path in backups:
        if path and os.path.exists(path):
            print(f"恢复: {feature}...", end=" ")
            true_rollback(feature, path)
            print("✅")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            list_backups()
        elif sys.argv[1] == "rollback" and len(sys.argv) > 2:
            # rollback 功能名 备份路径
            true_rollback(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
        elif sys.argv[1] == "emergency":
            emergency_restore()
    else:
        list_backups()
