# -*- coding: utf-8 -*-
"""
序境系统 - 核心功能测试
"""
import sys
import sqlite3
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony')
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'

print("="*60)
print("【核心功能测试】")
print("="*60)

# 测试数据库连接
print("\n【1. 数据库连接测试】")
try:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM 模型配置表")
    print(f"  ✅ 模型配置表: {c.fetchone()[0]}条")
    c.execute("SELECT COUNT(*) FROM 官署角色表")
    print(f"  ✅ 官署角色表: {c.fetchone()[0]}条")
    c.execute("SELECT COUNT(*) FROM 序境系统总则")
    print(f"  ✅ 序境系统总则: {c.fetchone()[0]}条")
    conn.close()
except Exception as e:
    print(f"  ❌ 数据库错误: {e}")

# 测试调度器
print("\n【2. 调度器测试】")
try:
    from dynamic_dispatcher import DynamicDispatcher
    dispatcher = DynamicDispatcher(db_path)
    print(f"  ✅ 调度器加载: {len(dispatcher.models)}个模型")
except Exception as e:
    print(f"  ❌ 调度器错误: {e}")

# 测试模型调用
print("\n【3. 模型调用测试】")
import requests
try:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT 模型名称, 模型标识符, API地址, API密钥 FROM 模型配置表 WHERE 服务商='火山引擎' LIMIT 1")
    row = c.fetchone()
    conn.close()
    
    if row:
        name, identifier, url, key = row
        if '/chat/completions' not in url:
            url = url.rstrip('/') + '/chat/completions'
        
        resp = requests.post(url, json={
            "model": identifier,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 10
        }, headers={"Authorization": f"Bearer {key}"}, timeout=20)
        
        if resp.status_code == 200:
            print(f"  ✅ {name}: 调用成功")
        else:
            print(f"  ❌ {name}: {resp.status_code}")
except Exception as e:
    print(f"  ❌ 调用错误: {e}")

# 测试Skill加载
print("\n【4. Skill加载测试】")
skill_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/Kernel/skills'
try:
    import os
    skills = [f for f in os.listdir(skill_path) if f.endswith('.py')]
    print(f"  ✅ Skill数量: {len(skills)}个")
    for s in skills[:5]:
        print(f"    - {s}")
except Exception as e:
    print(f"  ❌ Skill错误: {e}")

print("\n" + "="*60)
print("【测试完成】")
print("="*60)
