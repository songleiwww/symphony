#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统 - 第2级升级：健康检测 + 熔断机制
"""
import sqlite3
import time
from datetime import datetime

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

def create_health_table():
    """创建模型健康检测表"""
    print("\n【1】创建健康检测表")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 检查是否已存在
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='模型健康表'")
    if c.fetchone():
        print("  模型健康表已存在")
        conn.close()
        return
    
    # 创建健康检测表
    c.execute('''
        CREATE TABLE 模型健康表 (
            模型ID TEXT PRIMARY KEY,
            模型名称 TEXT,
            服务商 TEXT,
            健康状态 TEXT DEFAULT '未知',
            失败次数 INTEGER DEFAULT 0,
            连续失败 INTEGER DEFAULT 0,
            上次检测时间 REAL,
            API响应时间 REAL,
            熔断状态 TEXT DEFAULT '正常',
            创建时间 REAL,
            更新时间 REAL
        )
    ''')
    
    # 初始化现有模型
    c.execute('SELECT id, 模型名称, 服务商 FROM 模型配置表')
    models = c.fetchall()
    
    now = time.time()
    for m in models:
        c.execute('''
            INSERT INTO 模型健康表 (模型ID, 模型名称, 服务商, 健康状态, 创建时间, 更新时间)
            VALUES (?, ?, ?, '未知', ?, ?)
        ''', (m[0], m[1], m[2], now, now))
    
    conn.commit()
    print(f"  已初始化 {len(models)} 个模型健康记录")
    conn.close()

def create_circuit_breaker_table():
    """创建熔断记录表"""
    print("\n【2】创建熔断记录表")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 检查是否已存在
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='熔断记录表'")
    if c.fetchone():
        print("  熔断记录表已存在")
        conn.close()
        return
    
    # 创建熔断记录表
    c.execute('''
        CREATE TABLE 熔断记录表 (
            记录ID TEXT PRIMARY KEY,
            模型ID TEXT,
            熔断原因 TEXT,
            熔断时间 REAL,
            恢复时间 REAL,
            状态 TEXT DEFAULT '已熔断'
        )
    ''')
    
    conn.commit()
    print("  熔断记录表创建成功")
    conn.close()

def add_health_check_rules():
    """添加健康检测规则到内核规则表"""
    print("\n【3】添加健康检测规则")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    rule_content = '''【健康检测规则】
1. 每次调用前检测模型健康状态
2. 连续失败3次自动熔断
3. 熔断后自动切换备用模型
4. 熔断后每10分钟检测一次恢复
5. 恢复成功自动解除熔断'''
    
    # 检查是否已有规则
    c.execute("SELECT id FROM 内核规则表 WHERE id='rule_006'")
    if not c.fetchone():
        c.execute('''
            INSERT INTO 内核规则表 (id, 规则名称, 规则内容, 优先级, 状态, 创建时间, 更新时间)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('rule_006', '健康检测规则', rule_content, 1, '启用', 
              datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
              datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        print("  健康检测规则已添加")
    else:
        print("  健康检测规则已存在")
    
    conn.close()

def show_current_health():
    """显示当前健康状态"""
    print("\n【4】当前健康状态")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT 健康状态, COUNT(*) FROM 模型健康表 GROUP BY 健康状态')
    stats = c.fetchall()
    
    print("  健康统计:")
    for s in stats:
        print(f"    {s[0]}: {s[1]}")
    
    conn.close()

def full_upgrade():
    """完整升级流程"""
    print("="*60)
    print("序境系统 - 第2级升级：健康检测 + 熔断机制")
    print("="*60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 执行升级
    create_health_table()
    create_circuit_breaker_table()
    add_health_check_rules()
    show_current_health()
    
    print("\n" + "="*60)
    print("✅ 第2级升级完成：健康检测 + 熔断机制")
    print("="*60)

if __name__ == "__main__":
    full_upgrade()
