# -*- coding: utf-8 -*-
"""
序境系统 - Token真实消耗统计
遵循序境系统总则第24条：必须使用实际API返回的usage字段
"""
import sqlite3
import requests
import sys
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'

def test_model_with_token_stats(model_info):
    """测试模型并获取真实token消耗"""
    url = model_info['url']
    if '/chat/completions' not in url:
        url = url.rstrip('/') + '/chat/completions'
    
    test_prompt = "用一句话介绍你自己"
    
    try:
        resp = requests.post(url, json={
            "model": model_info['identifier'],
            "messages": [{"role": "user", "content": test_prompt}],
            "max_tokens": 50
        }, headers={"Authorization": f"Bearer {model_info['key']}", "Content-Type": "application/json"}, timeout=30)
        
        if resp.status_code == 200:
            data = resp.json()
            # 提取真实usage
            usage = data.get('usage', {})
            return {
                'success': True,
                'prompt_tokens': usage.get('prompt_tokens', 0),
                'completion_tokens': usage.get('completion_tokens', 0),
                'total_tokens': usage.get('total_tokens', 0),
                'model': model_info['name'],
                'provider': model_info['provider']
            }
        else:
            return {'success': False, 'error': resp.status_code, 'model': model_info['name']}
    except Exception as e:
        return {'success': False, 'error': str(e), 'model': model_info['name']}

# 连接数据库
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("="*60)
print("【Token真实消耗统计】")
print("="*60)

# 测试各服务商模型
providers = ['英伟达', '硅基流动', '火山引擎', '智谱', '魔搭', '魔力方舟']

total_prompt = 0
total_completion = 0
total_count = 0

results = []

for provider in providers:
    c.execute("SELECT 模型名称, 模型标识符, API地址, API密钥 FROM 模型配置表 WHERE 服务商=? AND 在线状态='online' LIMIT 1", (provider,))
    row = c.fetchone()
    if row:
        model_info = {
            'name': row[0],
            'identifier': row[1],
            'url': row[2],
            'key': row[3],
            'provider': provider
        }
        
        print(f"\n测试 {provider} - {model_info['name']}...", end=" ")
        result = test_model_with_token_stats(model_info)
        
        if result['success']:
            print(f"✅")
            print(f"  输入: {result['prompt_tokens']} tokens")
            print(f"  输出: {result['completion_tokens']} tokens")
            print(f"  总计: {result['total_tokens']} tokens")
            
            total_prompt += result['prompt_tokens']
            total_completion += result['completion_tokens']
            total_count += 1
            
            results.append(result)
        else:
            print(f"❌ {result.get('error')}")

print("\n" + "="*60)
print("【统计汇总】")
print("="*60)

print(f"测试模型数: {total_count}")
print(f"总输入Token: {total_prompt}")
print(f"总输出Token: {total_completion}")
print(f"总Token: {total_prompt + total_completion}")

# 保存到数据库
if results:
    print("\n【保存到数据库】")
    for r in results:
        c.execute("""INSERT INTO 模型执行结果表 
            (session_id, step, model_name, user_input, assistant_output, cost, prompt_tokens, status, error_msg, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (f"token_test_{datetime.now().strftime('%Y%m%d%H%M%S')}",
             total_count,
             r['model'],
             "token测试",
             "token测试",
             0,
             r['total_tokens'],
             'success',
             None,
             datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    conn.commit()
    print("✅ 已保存")

conn.close()
print("\n【完成】")
