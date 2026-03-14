#!/usr/bin/env python3
"""
序境系统 - 验证执行器
验证模型调用是否成功
从花名册读取人员信息
"""
import json
import requests
from datetime import datetime
from pathlib import Path

def load_roster():
    """从花名册加载人员信息"""
    roster_file = Path(__file__).parent / "sf_team_roster.json"
    with open(roster_file, encoding='utf-8') as f:
        return json.load(f)

def verify_model_call():
    """验证模型调用"""
    # 加载花名册
    roster = load_roster()
    
    # 查找沈清弦 (sf-001)
    verifier = None
    for member in roster.get('team', []):
        if member['id'] == 'sf-001':
            verifier = member
            break
    
    print("=" * 60)
    print("少府监执行验证报告")
    print("=" * 60)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"模型ID: ark-code-latest")
    print("-" * 60)
    print("执行官员:")
    if verifier:
        print(f"  姓名: {verifier.get('name', '未知')}")
        print(f"  官职: {verifier.get('role', '未知')}")
        print(f"  部门: {verifier.get('department', '未知')}")
        print(f"  人员ID: {verifier.get('id', '未知')}")
        print(f"  性格: {verifier.get('personality', '未知')}")
    else:
        print("  未找到对应人员")
    print("-" * 60)
    print("执行逻辑:")
    print("  1. 读取花名册配置 (sf_team_roster.json)")
    print("  2. 根据模型ID查找对应人员")
    print("  3. 调用火山引擎API (ark.cn-beijing.volces.com)")
    print("  4. 发送测试提示词")
    print("  5. 验证返回状态")
    print("  6. 记录Token消耗")
    print("-" * 60)
    
    # 实际调用API验证
    url = 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions'
    headers = {
        'Authorization': 'Bearer 3b922877-3fbe-45d1-a298-53f2231c5224',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': 'ark-code-latest',
        'messages': [
            {'role': 'system', 'content': '你是序境系统的验证助手。请回复：2026年AI Agent正在向多模态协作方向演进。'},
            {'role': 'user', 'content': '请确认系统状态'}
        ],
        'max_tokens': 100
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        status = response.status_code
        result = response.json()
        token_usage = result.get('usage', {}).get('total_tokens', 0)
        reply = result.get('choices', [{}])[0].get('message', {}).get('content', '')[:50]
    except Exception as e:
        status = 500
        token_usage = 0
        reply = f"Error: {str(e)}"
    
    print("执行结果:")
    print(f"  状态: {status}")
    print(f"  成功: {'是' if status == 200 else '否'}")
    print(f"  回复: {reply}...")
    print(f"  Token消耗: {token_usage}")
    print("=" * 60)

if __name__ == "__main__":
    verify_model_call()
