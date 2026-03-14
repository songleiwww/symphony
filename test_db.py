#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import sqlite3

# 直接测试数据库
db_path = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db"

print("Testing Symphony Database...")
print("=" * 50)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查官属角色表
    cursor.execute("SELECT COUNT(*) FROM 官属角色表")
    roles_count = cursor.fetchone()[0]
    print(f"Roles count: {roles_count}")
    
    # 检查模型配置表
    cursor.execute("SELECT COUNT(*) FROM 模型配置表")
    models_count = cursor.fetchone()[0]
    print(f"Models count: {models_count}")
    
    # 检查任务表
    cursor.execute("SELECT COUNT(*) FROM 任务表")
    tasks_count = cursor.fetchone()[0]
    print(f"Tasks count: {tasks_count}")
    
    # 检查记忆表
    cursor.execute("SELECT COUNT(*) FROM 记忆表")
    memory_count = cursor.fetchone()[0]
    print(f"Memory count: {memory_count}")
    
    conn.close()
    
    print("=" * 50)
    print("Database OK!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
