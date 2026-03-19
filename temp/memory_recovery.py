#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统 - 记忆接续解决方案
每天启动时自动加载核心规则
"""
import sqlite3
from datetime import datetime
import time

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

def load_core_rules():
    """第1步: 从内核规则表加载核心规则"""
    print("=" * 60)
    print("🔄 记忆接续 - 第1步: 加载核心规则")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT 规则名称, 规则内容 FROM 内核规则表 WHERE 状态='启用' ORDER BY 优先级 DESC")
    rules = c.fetchall()
    
    print(f"\n加载了 {len(rules)} 条核心规则:")
    for name, content in rules:
        # 写入记忆表
        memory_id = f"rule_{int(time.time())}"
        c.execute("""
            INSERT INTO 记忆表 (memory_id, content, memory_type, importance, source, created_at)
            VALUES (?, ?, 'core_rule', 1.0, 'kernel_rules', ?)
        """, (memory_id, f"{name}: {content[:200]}", time.time()))
        print(f"  ✅ {name}")
    
    conn.commit()
    conn.close()
    return len(rules)

def load_three_tables():
    """第2步: 加载三大表关键信息"""
    print("\n" + "=" * 60)
    print("🔄 记忆接续 - 第2步: 加载三大表信息")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 加载官署信息
    c.execute("SELECT id, 名称, 官品 FROM 官署表")
    offices = c.fetchall()
    print(f"\n官署表: {len(offices)}个官署")
    for o in offices:
        print(f"  ✅ {o[1]}({o[0]})")
    
    # 加载核心角色绑定
    c.execute("""
        SELECT r.姓名, r.官职, o.名称, m.模型名称, m.服务商
        FROM 官署角色表 r
        JOIN 官署表 o ON r.所属官署 = o.id
        JOIN 模型配置表 m ON r.模型配置表_ID = m.id
        WHERE r.id IN ('role-1', 'role-10', 'role-11')
    """)
    
    print("\n核心角色绑定:")
    for row in c.fetchall():
        print(f"  ✅ {row[0]}({row[1]}) -> {row[3]}({row[4]})")
    
    conn.close()
    return len(offices)

def load_today_tasks():
    """第3步: 检查今日任务"""
    print("\n" + "=" * 60)
    print("🔄 记忆接续 - 第3步: 检查今日任务")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 检查今日调度历史
    c.execute("""
        SELECT COUNT(*) FROM 调度历史表 
        WHERE timestamp LIKE ?
    """, (f"{today}%",))
    count = c.fetchone()[0]
    
    print(f"\n今日调度次数: {count}")
    
    # 检查待处理任务
    c.execute("SELECT COUNT(*) FROM 任务表 WHERE status='pending'")
    pending = c.fetchone()[0]
    print(f"待处理任务: {pending}")
    
    conn.close()
    return count, pending

def test_dispatch():
    """第4步: 测试调度逻辑"""
    print("\n" + "=" * 60)
    print("🔄 记忆接续 - 第4步: 测试调度逻辑")
    print("=" * 60)
    
    # 使用正确的三表关联
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""
        SELECT r.姓名, r.官职, o.名称 as 官署, m.模型名称, m.服务商
        FROM 官署角色表 r
        JOIN 官署表 o ON r.所属官署 = o.id
        JOIN 模型配置表 m ON r.模型配置表_ID = m.id
        WHERE r.id = 'role-1'
    """)
    
    row = c.fetchone()
    
    print(f"\n调度测试:")
    print(f"  角色: {row[0]}")
    print(f"  官职: {row[1]}")
    print(f"  官署: {row[2]}")
    print(f"  模型: {row[3]}")
    print(f"  引擎: {row[4]}")
    
    conn.close()
    return True

def full_recovery():
    """完整记忆接续流程"""
    print("\n" + "=" * 60)
    print("🚀 序境系统 - 记忆接续完整流程")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 加载核心规则
    rules_count = load_core_rules()
    
    # 2. 加载三大表
    offices_count = load_three_tables()
    
    # 3. 检查今日任务
    dispatch_count, pending = load_today_tasks()
    
    # 4. 测试调度
    dispatch_ok = test_dispatch()
    
    # 总结
    print("\n" + "=" * 60)
    print("✅ 记忆接续完成")
    print("=" * 60)
    print(f"  核心规则: {rules_count}条")
    print(f"  官署: {offices_count}个")
    print(f"  今日调度: {dispatch_count}次")
    print(f"  待处理任务: {pending}个")
    print(f"  调度测试: {'通过' if dispatch_ok else '失败'}")
    
    return {
        "rules": rules_count,
        "offices": offices_count,
        "dispatch": dispatch_count,
        "pending": pending,
        "dispatch_test": dispatch_ok
    }

if __name__ == "__main__":
    full_recovery()
