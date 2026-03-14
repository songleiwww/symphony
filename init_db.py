#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统数据库初始化脚本
创建所有必要的数据表
"""
import sqlite3
import os
import sys
import json

db_path = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db"

def init_tables():
    """初始化所有数据表"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Creating tables...")
    
    # 1. 官属角色表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS 官属角色表 (
        id TEXT PRIMARY KEY,
        姓名 TEXT NOT NULL,
        性别 TEXT,
        官职 TEXT,
        职务 TEXT,
        描述 TEXT,
        模型名称 TEXT,
        模型服务商 TEXT,
        角色等级 INTEGER DEFAULT 1,
        状态 TEXT DEFAULT '正常',
        创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("  - 官属角色表")
    
    # 2. 权限表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS 权限表 (
        id TEXT PRIMARY KEY,
        权限名称 TEXT NOT NULL,
        权限描述 TEXT,
        权限类型 TEXT DEFAULT '功能',
        状态 TEXT DEFAULT '正常'
    )
    ''')
    print("  - 权限表")
    
    # 3. 角色权限关联表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS 角色权限关联表 (
        角色ID TEXT,
        权限ID TEXT,
        授权时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        授权人 TEXT,
        PRIMARY KEY (角色ID, 权限ID)
    )
    ''')
    print("  - 角色权限关联表")
    
    # 4. 操作日志表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS 操作日志表 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        角色ID TEXT,
        操作类型 TEXT NOT NULL,
        操作内容 TEXT,
        操作时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        IP地址 TEXT,
        操作结果 TEXT DEFAULT '成功'
    )
    ''')
    print("  - 操作日志表")
    
    # 5. 任务表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS 任务表 (
        task_id TEXT PRIMARY KEY,
        content TEXT NOT NULL,
        task_type TEXT DEFAULT '通用任务',
        priority INTEGER DEFAULT 3,
        status TEXT DEFAULT 'pending',
        created_by TEXT DEFAULT 'system',
        created_at REAL NOT NULL,
        started_at REAL,
        completed_at REAL,
        parent_task_id TEXT,
        features TEXT,
        metadata TEXT
    )
    ''')
    print("  - 任务表")
    
    # 6. 任务结果表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS 任务结果表 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id TEXT NOT NULL,
        role_id TEXT NOT NULL,
        result_content TEXT,
        token_usage INTEGER DEFAULT 0,
        duration REAL DEFAULT 0,
        success INTEGER DEFAULT 1,
        created_at REAL NOT NULL
    )
    ''')
    print("  - 任务结果表")
    
    # 7. 任务错误表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS 任务错误表 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id TEXT NOT NULL,
        error_message TEXT NOT NULL,
        error_type TEXT,
        created_at REAL NOT NULL
    )
    ''')
    print("  - 任务错误表")
    
    # 8. 记忆表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS 记忆表 (
        memory_id TEXT PRIMARY KEY,
        content TEXT NOT NULL,
        memory_type TEXT DEFAULT 'short_term',
        importance REAL DEFAULT 0.5,
        source TEXT DEFAULT 'user',
        tags TEXT,
        created_at REAL NOT NULL,
        last_accessed REAL NOT NULL,
        access_count INTEGER DEFAULT 0,
        expires_at REAL,
        metadata TEXT
    )
    ''')
    print("  - 记忆表")
    
    # 9. 故障记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS 故障记录表 (
        fault_id TEXT PRIMARY KEY,
        fault_type TEXT NOT NULL,
        model_name TEXT NOT NULL,
        error_message TEXT,
        timestamp REAL NOT NULL,
        retry_count INTEGER DEFAULT 0,
        resolved INTEGER DEFAULT 0
    )
    ''')
    print("  - 故障记录表")
    
    # 10. 熔断器状态表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS 熔断器状态表 (
        model_name TEXT PRIMARY KEY,
        state TEXT DEFAULT 'closed',
        failure_count INTEGER DEFAULT 0,
        last_failure_time REAL,
        last_success_time REAL,
        updated_at REAL
    )
    ''')
    print("  - 熔断器状态表")
    
    # 11. 调度历史表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS 调度历史表 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id TEXT,
        role_id TEXT,
        model_name TEXT,
        score INTEGER,
        success INTEGER DEFAULT 1,
        timestamp REAL
    )
    ''')
    print("  - 调度历史表")
    
    conn.commit()
    conn.close()
    
    print("\nAll tables created successfully!")

def init_sample_data():
    """初始化示例数据"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查是否已有角色数据
    cursor.execute("SELECT COUNT(*) FROM 官属角色表")
    if cursor.fetchone()[0] > 0:
        print("\nSample data already exists, skipping...")
        conn.close()
        return
    
    print("\nAdding sample roles...")
    
    # 添加示例官属角色
    sample_roles = [
        {"id": "role_001", "姓名": "王安石", "官职": "参知政事", "职务": "变法主导", "模型名称": "glm-4.7", "模型服务商": "火山引擎", "角色等级": 3},
        {"id": "role_002", "姓名": "苏轼", "官职": "翰林学士", "职务": "文学创作", "模型名称": "glm-4.7", "模型服务商": "火山引擎", "角色等级": 2},
        {"id": "role_003", "姓名": "欧阳修", "官职": "参知政事", "职务": "文坛领袖", "模型名称": "Qwen2.5-14B", "模型服务商": "硅基流动", "角色等级": 3},
        {"id": "role_004", "姓名": "韩愈", "官职": "吏部侍郎", "职务": "古文运动", "模型名称": "glm-4-flash", "模型服务商": "智谱", "角色等级": 2},
        {"id": "role_005", "姓名": "柳宗元", "官职": "永州司马", "职务": "思想家", "模型名称": "glm-4-flash", "模型服务商": "智谱", "角色等级": 2},
    ]
    
    for role in sample_roles:
        cursor.execute('''
        INSERT INTO 官属角色表 (id, 姓名, 官职, 职务, 模型名称, 模型服务商, 角色等级, 状态)
        VALUES (?, ?, ?, ?, ?, ?, ?, '正常')
        ''', (role["id"], role["姓名"], role["官职"], role["职务"], 
              role["模型名称"], role["模型服务商"], role["角色等级"]))
    
    conn.commit()
    conn.close()
    
    print(f"  Added {len(sample_roles)} sample roles")

if __name__ == "__main__":
    print("=" * 60)
    print("Symphony Database Initialization")
    print("=" * 60)
    
    init_tables()
    init_sample_data()
    
    print("\n" + "=" * 60)
    print("Initialization Complete!")
    print("=" * 60)
