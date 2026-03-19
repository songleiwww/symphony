# -*- coding: utf-8 -*-
"""
内核自动初始化 - 如果Kernel文件夹不存在则创建
基于 symphony.db 数据组织多模态协作
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
KERNEL_DIR = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/Kernel'

def ensure_kernel_exists():
    """确保内核存在，如不存在则创建"""
    if not os.path.exists(KERNEL_DIR):
        print(f"⚠️ 内核目录不存在，正在创建: {KERNEL_DIR}")
        os.makedirs(KERNEL_DIR, exist_ok=True)
        create_kernel_files()
    else:
        print(f"✅ 内核目录已存在: {KERNEL_DIR}")
    
    # 验证内核配置
    verify_kernel()

def create_kernel_files():
    """基于数据库创建内核文件"""
    print("📝 基于 symphony.db 创建内核文件...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查必要表
    required_tables = ['官署表', '官署角色表', '模型配置表', '内核规则表']
    for table in required_tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if not cursor.fetchone():
            print(f"  ❌ 缺少表: {table}")
        else:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  ✅ {table}: {count} 条")
    
    conn.close()

def verify_kernel():
    """验证内核配置"""
    print("\n=== 内核验证 ===")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 规则检查
    cursor.execute("SELECT 规则名称, 规则内容 FROM 内核规则表 WHERE 状态='启用'")
    rules = cursor.fetchall()
    print(f"内核规则 ({len(rules)}):")
    for name, content in rules:
        print(f"  • {name}: {content}")
    
    # 数据检查
    cursor.execute("SELECT COUNT(*) FROM 官署表")
    offices = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM 官署角色表")
    office_roles = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM 模型配置表")
    models = cursor.fetchone()[0]
    
    print(f"\n数据统计:")
    print(f"  • 官署: {offices} 个")
    print(f"  • 官署角色: {office_roles} 人")
    print(f"  • 模型: {models} 个")
    
    conn.close()

if __name__ == "__main__":
    ensure_kernel_exists()
