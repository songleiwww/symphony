#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统 - 接管上级AI的正确调度逻辑
从官署角色表 → 模型配置表 → 真实API调用
"""
import sqlite3
import requests
from datetime import datetime

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

def get_official_model(role_id):
    """第1步: 从官署角色表读取模型配置表_ID"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""
        SELECT r.id, r.姓名, r.官职, r.模型配置表_ID
        FROM 官署角色表 r
        WHERE r.id = ?
    """, (role_id,))
    
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            "role_id": row[0],
            "name": row[1],
            "title": row[2],
            "model_config_id": row[3]
        }
    return None

def get_api_config(model_config_id):
    """第2步: 关联模型配置表获取API配置"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""
        SELECT id, 模型名称, 模型标识符, 服务商, API地址, API密钥
        FROM 模型配置表
        WHERE id = ?
    """, (model_config_id,))
    
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

def call_api(api_config, prompt):
    """第3步: 真实API调用"""
    headers = {
        "Authorization": f"Bearer {api_config['api_key']}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": api_config["api_id"],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 150
    }
    
    try:
        resp = requests.post(api_config["api_url"], headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            content = result["choices"][0]["message"]["content"]
            return {"success": True, "response": content}
        else:
            return {"success": False, "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def dispatch(user_input, role_id="role-1"):
    """完整调度流程"""
    print("=" * 60)
    print("🔄 序境系统 - 接管上级AI调度")
    print("=" * 60)
    
    # 步骤1: 获取官员信息
    print("\n📋 步骤1: 官署角色表")
    official = get_official_model(role_id)
    if not official:
        print("❌ 未找到官员")
        return
    
    print(f"   角色ID: {official['role_id']}")
    print(f"   姓名: {official['name']}")
    print(f"   官职: {official['title']}")
    print(f"   模型配置ID: {official['model_config_id']}")
    
    # 步骤2: 获取API配置
    print("\n📋 步骤2: 模型配置表")
    api_config = get_api_config(official['model_config_id'])
    if not api_config:
        print("❌ 未找到模型配置")
        return
    
    print(f"   模型名称: {api_config['name']}")
    print(f"   模型标识符: {api_config['api_id']}")
    print(f"   服务商: {api_config['provider']}")
    print(f"   API地址: {api_config['api_url'][:50]}...")
    
    # 步骤3: 真实API调用
    print("\n📋 步骤3: 真实API调用")
    print(f"   输入: {user_input}")
    
    result = call_api(api_config, user_input)
    
    if result["success"]:
        print(f"   ✅ 成功!")
        print(f"   响应: {result['response'][:100]}...")
        return result
    else:
        print(f"   ❌ 错误: {result['error']}")
        return result

if __name__ == "__main__":
    # 测试调度 - 陆念昭
    result = dispatch("你好，请用一句话介绍序境系统", "role-1")
