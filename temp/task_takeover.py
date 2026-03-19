#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统 - 任务接管工作流
接管上级AI的任务，实际执行
"""
import sqlite3
import requests
import os
import json
from datetime import datetime
from datetime import datetime

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

def get_pending_tasks():
    """获取待处理任务"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT task_id, content, task_type, priority, status FROM 任务表 WHERE status = 'pending' ORDER BY priority DESC")
    tasks = c.fetchall()
    conn.close()
    return tasks

def get_official_for_task(task_type):
    """根据任务类型分配官员"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 任务类型映射到官署
    mapping = {
        '通用任务': 'SELECT id, 姓名, 官职, 模型配置表_ID FROM 官署角色表 WHERE 状态="正常" LIMIT 1',
        '搜索任务': 'SELECT id, 姓名, 官职, 模型配置表_ID FROM 官署角色表 WHERE 官职 LIKE "%尚令%" LIMIT 1',
        '数据分析': 'SELECT id, 姓名, 官职, 模型配置表_ID FROM 官署角色表 WHERE 官职="少府监" LIMIT 1',
    }
    
    query = mapping.get(task_type, mapping['通用任务'])
    c.execute(query)
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            'role_id': row[0],
            'name': row[1],
            'title': row[2],
            'model_id': row[3]
        }
    return None

def get_model_config(model_id):
    """获取模型配置"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, 模型名称, 模型标识符, 服务商, API地址, API密钥 FROM 模型配置表 WHERE id = ?", (model_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "api_id": row[2],
            "provider": row[3],
            "api_url": row[4],
            "api_key": row[5]
        }
    return None

def call_model(model_config, prompt):
    """调用模型"""
    api_key = os.getenv("VOLCANO_API_KEY", "")
    
    if not api_key:
        # 尝试火山引擎
        url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_config["api_id"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500
        }
        
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                return {"success": True, "result": resp.json()}
            else:
                return {"success": False, "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    return {"success": False, "error": "No API key"}

def record_dispatch(task_id, role_id, model_name, score, success):
    """记录调度历史"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO 调度历史表 (task_id, role_id, model_name, score, success, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (task_id, role_id, model_name, score, success, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def update_task_status(task_id, status, result=None):
    """更新任务状态"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if result:
        c.execute("UPDATE 任务表 SET status = ?, result = ? WHERE task_id = ?", (status, result, task_id))
    else:
        c.execute("UPDATE 任务表 SET status = ? WHERE task_id = ?", (status, task_id))
    conn.commit()
    conn.close()

def process_all_tasks():
    """处理所有待办任务"""
    print("=" * 60)
    print("🔄 序境系统 - 接管任务处理")
    print("=" * 60)
    
    # 1. 获取待处理任务
    tasks = get_pending_tasks()
    print(f"\n📋 待处理任务: {len(tasks)}个")
    
    if not tasks:
        print("✅ 无待处理任务")
        return
    
    # 2. 逐个处理
    for task in tasks:
        task_id, content, task_type, priority, status = task
        print(f"\n{'='*40}")
        print(f"📌 任务: {task_id}")
        print(f"   内容: {content}")
        print(f"   类型: {task_type}")
        print(f"   优先级: {priority}")
        
        # 3. 分配官员 (第1集: 模型治理)
        official = get_official_for_task(task_type)
        if not official:
            print("   ❌ 无可用官员")
            update_task_status(task_id, "failed", "No available official")
            continue
        
        print(f"   👤 官员: {official['name']}({official['title']})")
        
        # 4. 获取模型配置
        model_config = get_model_config(official['model_id'])
        if not model_config:
            print("   ❌ 无可用模型")
            update_task_status(task_id, "failed", "No available model")
            continue
        
        print(f"   🤖 模型: {model_config['name']}({model_config['provider']})")
        
        # 5. 实际调用 (第2-3集)
        result = call_model(model_config, content)
        
        if result["success"]:
            try:
                response = result["result"]["choices"][0]["message"]["content"]
                print(f"   ✅ 响应: {response[:100]}...")
                score = 1
                # 记录
                record_dispatch(task_id, official['role_id'], model_config['api_id'], score, 1)
                update_task_status(task_id, "completed", response[:500])
            except Exception as e:
                print(f"   ❌ 解析错误: {e}")
                score = 0
                record_dispatch(task_id, official['role_id'], model_config['api_id'], score, 0)
                update_task_status(task_id, "failed", str(e))
        else:
            print(f"   ❌ 调用失败: {result.get('error')}")
            record_dispatch(task_id, official['role_id'], model_config['api_id'], 0, 0)
            update_task_status(task_id, "failed", result.get('error'))
    
    print("\n" + "=" * 60)
    print("✅ 任务处理完成")
    print("=" * 60)

if __name__ == "__main__":
    process_all_tasks()
