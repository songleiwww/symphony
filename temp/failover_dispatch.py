#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统 - 故障转移机制
当API调用错误时，自动切换到有效的备用人员
"""
import sqlite3
import requests
from datetime import datetime

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

def get_valid_officials():
    """获取所有有效人员列表"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""
        SELECT r.id, r.姓名, r.官职, m.模型名称, m.模型标识符, m.API地址, m.API密钥, m.服务商
        FROM 官署角色表 r
        JOIN 模型配置表 m ON r.模型配置表_ID = m.id
        WHERE m.API地址 IS NOT NULL AND m.API密钥 IS NOT NULL
        AND r.状态 = '正常'
        ORDER BY r.id
    """)
    
    officials = []
    for row in c.fetchall():
        officials.append({
            "role_id": row[0],
            "name": row[1],
            "title": row[2],
            "model_name": row[3],
            "api_id": row[4],
            "api_url": row[5],
            "api_key": row[6],
            "provider": row[7]
        })
    
    conn.close()
    return officials

def test_api(official):
    """测试单个API是否可用"""
    headers = {"Authorization": f"Bearer {official['api_key']}", "Content-Type": "application/json"}
    payload = {"model": official["api_id"], "messages": [{"role": "user", "content": "hi"}], "max_tokens": 10}
    
    try:
        resp = requests.post(official["api_url"], headers=headers, json=payload, timeout=10)
        return resp.status_code == 200
    except:
        return False

def failover_dispatch(user_input, primary_role_id="role-1"):
    """
    故障转移调度
    1. 先尝试主角色
    2. 如果失败，依次尝试备用角色
    """
    print("=" * 70)
    print("🔄 故障转移调度")
    print("=" * 70)
    
    # 获取所有有效人员
    officials = get_valid_officials()
    print(f"\n有效人员总数: {len(officials)}")
    
    # 找到主角色索引
    primary_index = 0
    for i, off in enumerate(officials):
        if off["role_id"] == primary_role_id:
            primary_index = i
            break
    
    print(f"主角色: {officials[primary_index]['name']}({officials[primary_index]['title']})")
    print(f"模型: {officials[primary_index]['model_name']}({officials[primary_index]['provider']})")
    
    # 尝试调度
    print("\n【尝试调度】")
    
    # 按优先级尝试（主角色优先）
    tried = []
    
    # 先试主角色
    officials_try = [officials[primary_index]] + [o for i, o in enumerate(officials) if i != primary_index]
    
    for official in officials_try:
        print(f"\n尝试: {official['name']}({official['model_name']})...", end=" ")
        
        if test_api(official):
            print("✅ 可用!")
            
            # 实际调用
            headers = {"Authorization": f"Bearer {official['api_key']}", "Content-Type": "application/json"}
            payload = {"model": official["api_id"], "messages": [{"role": "user", "content": user_input}], "max_tokens": 100}
            
            try:
                resp = requests.post(official["api_url"], headers=headers, json=payload, timeout=30)
                if resp.status_code == 200:
                    result = resp.json()
                    content = result["choices"][0]["message"]["content"]
                    print(f"\n✅ 调度成功!")
                    print(f"   角色: {official['name']}")
                    print(f"   模型: {official['model_name']}")
                    print(f"   响应: {content[:80]}...")
                    return True
            except Exception as e:
                print(f"❌ 调用失败: {e}")
        else:
            print("❌ 不可用")
            tried.append(official["name"])
    
    print(f"\n❌ 所有{len(tried)+1}个角色都失败")
    return False

if __name__ == "__main__":
    # 测试故障转移
    failover_dispatch("你好，请用一句话介绍自己", "role-1")
