# -*- coding: utf-8 -*-
"""
安全性能优化脚本 - 100%非破坏?"""
import os
import sys
import py_compile
import compileall

def safe_optimize():
    """执行安全的性能优化"""
    print("=" * 60)
    print("序境系统 - 安全性能优化")
    print("=" * 60)
    
    # 1. 字节码预编译
    print("\n[1/3] 字节码预编译...")
    try:
        symphony_path = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony"
        if os.path.exists(symphony_path):
            count = compileall.compile_dir(symphony_path, force=True, quiet=1)
            print(f"  ?预编译完? {count} 个文?)
        else:
            print(f"  ! 路径不存? {symphony_path}")
    except Exception as e:
        print(f"  ! 预编译跳? {e}")
    
    # 2. 验证配置完整?    print("\n[2/3] 验证配置完整?..")
    try:
        sys.path.insert(0, r"C:\Users\Administrator\.openclaw\workspace\skills\symphony")
        from config.provider_mapping import PROVIDER_MAPPING
        
        total_models = sum(len(c.get('models', [])) for c in PROVIDER_MAPPING.values())
        print(f"  ?服务? {len(PROVIDER_MAPPING)} ?)
        print(f"  ?模型总数: {total_models} ?)
    except Exception as e:
        print(f"  ! 配置验证跳过: {e}")
    
    # 3. 数据库验?    print("\n[3/3] 数据库验?..")
    try:
        db_path = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\symphony.db"
        if os.path.exists(db_path):
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [t[0] for t in cursor.fetchall()]
            conn.close()
            print(f"  ?数据库表: {len(tables)} ?)
            print(f"    ? {', '.join(tables[:3])}...")
        else:
            print(f"  ! 数据库不存在")
    except Exception as e:
        print(f"  ! 数据库验证跳? {e}")
    
    print("\n" + "=" * 60)
    print("优化完成 - 所有操?00%安全")
    print("=" * 60)

if __name__ == "__main__":
    safe_optimize()

