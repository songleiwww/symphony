# -*- coding: utf-8 -*-
"""
多模型调度检测脚本
检测各服务商模型调用是否正常
"""
import sqlite3
import json
import time
import requests
from datetime import datetime

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

def get_all_models():
    """获取所有在线模型"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, 模型名称, API地址, API密钥, 服务商 FROM 模型配置表 WHERE 在线状态="online"')
    models = c.fetchall()
    conn.close()
    return models

def test_model(model_info):
    """测试单个模型"""
    model_id, name, url, api_key, provider = model_info
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': name,
        'messages': [{'role': 'user', 'content': '用一句话介绍你自己'}],
        'max_tokens': 50
    }
    
    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')[:80]
            tokens = result.get('usage', {}).get('total_tokens', 0)
            return {
                'success': True,
                'model': name,
                'provider': provider,
                'status_code': response.status_code,
                'tokens': tokens,
                'elapsed': round(elapsed, 2),
                'content': content
            }
        else:
            return {
                'success': False,
                'model': name,
                'provider': provider,
                'status_code': response.status_code,
                'error': response.text[:80]
            }
    except Exception as e:
        return {
            'success': False,
            'model': name,
            'provider': provider,
            'error': str(e)[:80]
        }

# 主测试
print("=" * 60)
print("多模型调度检测报告")
print("=" * 60)
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

models = get_all_models()
print(f"在线模型总数: {len(models)}\n")

# 按服务商分组测试
providers = {}
for m in models:
    p = m[4]
    if p not in providers:
        providers[p] = []
    providers[p].append(m)

results = []
for provider, model_list in providers.items():
    print(f"\n{'='*40}")
    print(f"服务商: {provider} ({len(model_list)}个模型)")
    print(f"{'='*40}")
    
    # 每个服务商测试1个模型
    model = model_list[0]
    print(f"\n测试模型: {model[1]}")
    print(f"API地址: {model[2]}")
    
    result = test_model(model)
    results.append(result)
    
    if result['success']:
        print(f"状态: ✅ 成功")
        print(f"Tokens: {result['tokens']}")
        print(f"耗时: {result['elapsed']}s")
        print(f"回复: {result['content'][:50]}...")
    else:
        print(f"状态: ❌ 失败 ({result['status_code']})")
        print(f"错误: {result.get('error', 'Unknown')[:50]}")

# 汇总
print("\n" + "=" * 60)
print("汇总")
print("=" * 60)

for provider in providers:
    provider_results = [r for r in results if r['provider'] == provider]
    success = sum(1 for r in provider_results if r['success'])
    print(f"{provider}: {success}/{len(provider_results)} 成功")

total_success = sum(1 for r in results if r['success'])
print(f"\n总计: {total_success}/{len(results)} 成功")
