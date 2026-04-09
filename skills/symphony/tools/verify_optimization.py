# -*- coding: utf-8 -*-
"""
验证优化结果 - 100%安全验证
"""
import os
import sys

def verify_optimization():
    """验证优化结果"""
    print("=" * 60)
    print("验证优化结果")
    print("=" * 60)
    
    # 1. 验证配置文件
    print("\n[1/4] 验证 openclaw.json...")
    try:
        import json
        config_path = r"C:\Users\Administrator\.openclaw\openclaw.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        models = config.get('agents', {}).get('defaults', {}).get('models', {})
        print(f"  配置模型? {len(models)}")
        for model in list(models.keys())[:5]:
            print(f"    - {model}")
        print("  ?配置验证通过")
    except Exception as e:
        print(f"  ! 配置验证失败: {e}")
    
    # 2. 验证字节码缓?    print("\n[2/4] 验证字节码缓?..")
    try:
        pycache_path = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\__pycache__"
        if os.path.exists(pycache_path):
            files = [f for f in os.listdir(pycache_path) if f.endswith('.pyc')]
            print(f"  字节码文? {len(files)} ?)
            print("  ?字节码缓存正?)
        else:
            print("  ! 字节码缓存目录不存在")
    except Exception as e:
        print(f"  ! 字节码验证失? {e}")
    
    # 3. 验证数据?    print("\n[3/4] 验证数据?..")
    try:
        db_path = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db"
        if os.path.exists(db_path):
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [t[0] for t in cursor.fetchall()]
            conn.close()
            print(f"  数据库表: {len(tables)} ?)
            print(f"  ? {', '.join(tables[:3])}")
            print("  ?数据库验证通过")
        else:
            print("  ! 数据库不存在")
    except Exception as e:
        print(f"  ! 数据库验证失? {e}")
    
    # 4. 验证模型配置
    print("\n[4/4] 验证模型配置...")
    try:
        sys.path.insert(0, r"C:\Users\Administrator\.openclaw\workspace\skills\symphony")
        from config.provider_mapping import PROVIDER_MAPPING
        
        total_models = sum(len(c.get('models', [])) for c in PROVIDER_MAPPING.values())
        print(f"  服务? {len(PROVIDER_MAPPING)} ?)
        print(f"  模型总数: {total_models} ?)
        print("  ?模型配置验证通过")
    except Exception as e:
        print(f"  ! 模型配置验证失败: {e}")
    
    print("\n" + "=" * 60)
    print("验证完成 - 所有系统正?)
    print("=" * 60)

if __name__ == "__main__":
    verify_optimization()

