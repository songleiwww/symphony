#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统 - 任务接管工作流 v2
"""
import sqlite3
import requests
import os
import json
from datetime import datetime

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

def get_pending_tasks():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT task_id, content, task_type, priority, status FROM 任务表 WHERE status = 'pending'")
    tasks = c.fetchall()
    conn.close()
    return tasks

def get_official_for_task(task_type):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, 姓名, 官职, 模型配置表_ID FROM 官署角色表 WHERE 状态="正常" LIMIT 1')
    row = c.fetchone()
    conn.close()
    if row:
        return {'role_id': row[0], 'name': row[1], 'title': row[2], 'model_id': row[3]}
    return None

def get_model_config(model_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, 模型名称, 模型标识符, 服务商, API地址, API密钥 FROM 模型配置表 WHERE id = ?", (model_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "api_id": row[2], "provider": row[3], "api_url": row[4], "api_key": row[5]}
    return None

def call_model_via_openrouter(model_config, prompt):
    """使用OpenRouter调用模型"""
    import requests
    
    # 使用OpenRouter作为中转
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY', '')}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://xujing.ai",
        "X-Title": "Xujing System"
    }
    
    # 映射到支持的模型
    model_map = {
        "doubao-seed-2.0-pro": "deepseek/deepseek-chat",
        "ark-code-latest": "deepseek/deepseek-chat"
    }
    
    model = model_map.get(model_config["api_id"], "deepseek/deepseek-chat")
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            return {"success": True, "result": resp.json()}
        else:
            return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text[:100]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def record_dispatch(task_id, role_id, model_name, score, success):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO 调度历史表 (task_id, role_id, model_name, score, success, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
        (task_id, role_id, model_name, score, success, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def update_task_status(task_id, status):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE 任务表 SET status = ? WHERE task_id = ?", (status, task_id))
    conn.commit()
    conn.close()

def process_tasks():
    print("=" * 50)
    print("🔄 序境系统 - 接管任务处理")
    print("=" * 50)
    
    tasks = get_pending_tasks()
    print(f"\n📋 待处理: {len(tasks)}个")
    
    if not tasks:
        print("✅ 无任务")
        return
    
    for task in tasks:
        task_id, content, task_type, priority, _ = task
        print(f"\n📌 任务: {task_id}")
        print(f"   内容: {content}")
        
        official = get_official_for_task(task_type)
        if not official:
            print("   ❌ 无官员")
            continue
        
        print(f"   👤 {official['name']}({official['title']})")
        
        model_config = get_model_config(official['model_id'])
        if not model_config:
            print("   ❌ 无模型")
            continue
        
        print(f"   🤖 {model_config['name']}")
        
        # 调用
        result = call_model_via_openrouter(model_config, content)
        
        if result["success"]:
            try:
                response = result["result"]["choices"][0]["message"]["content"]
                print(f"   ✅ {response[:80]}...")
                record_dispatch(task_id, official['role_id'], model_config['api_id'], 1, 1)
                update_task_status(task_id, "completed")
            except Exception as e:
                print(f"   ❌ 解析: {e}")
                record_dispatch(task_id, official['role_id'], model_config['api_id'], 0, 0)
                update_task_status(task_id, "failed")
        else:
            print(f"   ❌ {result.get('error')}")
            record_dispatch(task_id, official['role_id'], model_config['api_id'], 0, 0)
            update_task_status(task_id, "failed")
    
    print("\n" + "=" * 50)
    print("✅ 完成")
    print("=" * 50)

if __name__ == "__main__":
    process_tasks()
