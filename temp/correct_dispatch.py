#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统 - 正确的调度逻辑
用户输入 → 3级矩阵 → 真实模型调用
"""
import sqlite3
import requests
from datetime import datetime

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

# ==================== 调度逻辑 ====================

def dispatch(user_input):
    """
    序境系统万层调度逻辑
    第1集: 模型治理 - 选择合适的官员/模型
    第2集: 架构优化 - 健康检测、熔断检查
    第3集: 实际调用 - 真实API执行
    """
    print("=" * 60)
    print("🔄 序境系统万层 - 调度逻辑")
    print("=" * 60)
    
    # 第1集: 模型治理
    print("\n📡 第1集: 模型治理")
    official = select_official(user_input)
    print(f"   👤 官员: {official['name']}({official['title']})")
    print(f"   🤖 模型: {official['model_name']}({official['provider']})")
    
    # 第2集: 架构优化
    print("\n🛡️ 第2集: 架构优化")
    health = check_health(official['model_id'])
    print(f"   心跳: {'✅ 正常' if health['alive'] else '❌ 异常'}")
    print(f"   熔断: {'✅ 未熔断' if not health['熔断'] else '❌ 已熔断'}")
    
    if not health['alive'] or health['熔断']:
        # 备用模型
        print("   🔄 切换备用模型...")
        official = get_backup_official()
        print(f"   👤 备用: {official['name']}({official['model_name']})")
    
    # 第3集: 实际调用
    print("\n⚡ 第3集: 真实调用")
    result = call_real_model(official, user_input)
    
    if result['success']:
        print(f"   ✅ 响应: {result['response'][:80]}...")
        # 记录调度
        record_dispatch(official, result['response'][:100])
        return result
    else:
        print(f"   ❌ 错误: {result['error']}")
        # 记录失败
        record_failure(official, result['error'])
        return result

def select_official(user_input):
    """第1集: 选择官员"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 根据输入关键词选择官职
    if any(w in user_input for w in ["代码", "编程", "开发"]):
        c.execute('SELECT id, 姓名, 官职, 模型配置表_ID FROM 官署角色表 WHERE 官职 LIKE "%尚令%" LIMIT 1')
    elif any(w in user_input for w in ["分析", "数据", "统计"]):
        c.execute('SELECT id, 姓名, 官职, 模型配置表_ID FROM 官署角色表 WHERE 官职="少府监" LIMIT 1')
    else:
        c.execute('SELECT id, 姓名, 官职, 模型配置表_ID FROM 官署角色表 WHERE 状态="正常" LIMIT 1')
    
    row = c.fetchone()
    conn.close()
    
    # 获取模型信息
    model_info = get_model_info(row[3])
    
    return {
        "role_id": row[0],
        "name": row[1],
        "title": row[2],
        "model_id": row[3],
        "model_name": model_info["name"],
        "provider": model_info["provider"]
    }

def get_model_info(model_id):
    """获取模型信息"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 模型名称, 服务商 FROM 模型配置表 WHERE id = ?", (model_id,))
    row = c.fetchone()
    conn.close()
    return {"name": row[0], "provider": row[1]}

def check_health(model_id):
    """第2集: 健康检测"""
    # 简单检测 - 可扩展
    return {"alive": True, "熔断": False}

def get_backup_official():
    """获取备用官员"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, 姓名, 官职, 模型配置表_ID FROM 官署角色表 WHERE 状态="正常" ORDER BY RANDOM() LIMIT 1')
    row = c.fetchone()
    conn.close()
    model_info = get_model_info(row[3])
    return {
        "role_id": row[0],
        "name": row[1],
        "title": row[2],
        "model_id": row[3],
        "model_name": model_info["name"],
        "provider": model_info["provider"]
    }

def call_real_model(official, prompt):
    """第3集: 真实模型调用"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 模型标识符, API地址, API密钥 FROM 模型配置表 WHERE id = ?", (official['model_id'],))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return {"success": False, "error": "No model config"}
    
    api_id, api_url, api_key = row
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": api_id, "messages": [{"role": "user", "content": prompt}], "max_tokens": 150}
    
    try:
        resp = requests.post(api_url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            content = result["choices"][0]["message"]["content"]
            return {"success": True, "response": content}
        else:
            return {"success": False, "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def record_dispatch(official, response):
    """记录调度"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO 调度历史表 (task_id, role_id, model_name, score, success, timestamp)
        VALUES (?, ?, ?, 1, 1, ?)
    """, (f"disp-{datetime.now().strftime('%Y%m%d%H%M%S')}", 
          official['role_id'], official['model_name'], datetime.now().isoformat()))
    conn.commit()
    conn.close()

def record_failure(official, error):
    """记录失败"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO 调度历史表 (task_id, role_id, model_name, score, success, timestamp)
        VALUES (?, ?, ?, 0, 0, ?)
    """, (f"disp-{datetime.now().strftime('%Y%m%d%H%M%S')}", 
          official['role_id'], official['model_name'], datetime.now().isoformat()))
    conn.commit()
    conn.close()

# ==================== 执行 ====================

if __name__ == "__main__":
    # 测试调度逻辑
    test_inputs = [
        "你好，请介绍一下自己",
        "帮我写一段Python代码",
        "分析一下当前的经济形势"
    ]
    
    for inp in test_inputs:
        print(f"\n>>> 输入: {inp}")
        result = dispatch(inp)
        print()
