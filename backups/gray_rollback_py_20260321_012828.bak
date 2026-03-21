# -*- coding: utf-8 -*-
"""
序境系统 - 灰度回滚模块
"""
import sqlite3
from datetime import datetime

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db"

def create_backup(feature_name, backup_content, version="v1.0"):
    """创建功能备份"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT INTO 功能备份表 
        (功能名称, 备份版本, 备份时间, 备份内容, 状态) 
        VALUES (?, ?, ?, ?, ?)""",
        (feature_name, version, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), backup_content, 'active'))
    conn.commit()
    conn.close()
    print(f"✅ 备份已创建: {feature_name}")

def rollback(feature_name, target_version=None):
    """回滚到指定版本"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if target_version:
        c.execute("SELECT * FROM 功能备份表 WHERE 功能名称=? AND 备份版本=?", (feature_name, target_version))
    else:
        c.execute("SELECT * FROM 功能备份表 WHERE 功能名称=? ORDER BY id DESC LIMIT 1", (feature_name,))
    
    backup = c.fetchone()
    if backup:
        c.execute("UPDATE 功能备份表 SET 状态='已回滚' WHERE 功能名称=?", (feature_name,))
        conn.commit()
        print(f"✅ 已回滚: {feature_name} -> {backup[2]}")
        return backup
    else:
        print(f"❌ 未找到备份: {feature_name}")
        return None

def get_status():
    """获取灰度状态"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 功能名称, 备份版本, 状态, 灰度比例, 备份时间 FROM 功能备份表 ORDER BY id DESC")
    backups = c.fetchall()
    conn.close()
    
    print("\n" + "="*50)
    print("【灰度状态】")
    print("="*50)
    for b in backups:
        print(f"{b[0]}: {b[1]} | {b[2]} | 灰度{b[3]}% | {b[4]}")
    
    return backups

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            get_status()
        elif sys.argv[1] == "backup" and len(sys.argv) > 2:
            create_backup(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
        elif sys.argv[1] == "rollback" and len(sys.argv) > 2:
            rollback(sys.argv[2])
    else:
        get_status()
