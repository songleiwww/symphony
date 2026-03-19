# -*- coding: utf-8 -*-
import sqlite3
import json
import time
import requests
from datetime import datetime

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

def get_models_by_provider(provider):
    """获取指定服务商的模型"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT id, 模型名称, API地址, API密钥, 服务商, 在线状态 
                FROM 模型配置表 
                WHERE 在线状态="online" AND 服务商=? 
                LIMIT 3''', (provider,))
    models = c.fetchall()
    conn.close()
    return models

def test_model(model_info):
    """测试单个模型"""
    model_id, name, url, api_key, provider, status = model_info
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # 根据服务商调整payload
    if provider == '火山引擎':
        payload = {
            'model': name,
            'messages': [{'role': 'user', 'content': '用一句话介绍你自己'}],
            'max_tokens': 100
        }
    elif provider == '智谱':
        payload = {
            'model': name,
            'messages': [{'role': 'user', 'content': '用一句话介绍你自己'}]
        }
    else:
        payload = {
            'model': name,
            'messages': [{'role': 'user', 'content': '用一句话介绍你自己'}]
        }
    
    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')[:100]
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
                'error': response.text[:100]
            }
    except Exception as e:
        return {
            'success': False,
            'model': name,
            'provider': provider,
            'error': str(e)[:100]
        }

# 测试火山引擎模型
print("=== 火山引擎模型测试 ===\n")

models = get_models_by_provider('火山引擎')
print(f"测试 {len(models)} 个模型\n")

results = []
for i, model in enumerate(models, 1):
    print(f"[{i}] {model[1]}...")
    result = test_model(model)
    results.append(result)
    
    if result['success']:
        print(f"    状态: 成功")
        print(f"    Tokens: {result.get('tokens', 0)}")
        print(f"    耗时: {result.get('elapsed')}s")
        print(f"    回复: {result.get('content', '')[:50]}...")
    else:
        print(f"    状态: 失败 ({result.get('status_code')})")
        print(f"    错误: {result.get('error', 'Unknown')[:50]}")
    print()

# 统计
success_count = sum(1 for r in results if r['success'])
total_tokens = sum(r.get('tokens', 0) for r in results if r['success'])

print("=== 汇总 ===")
print(f"测试模型: {len(results)}")
print(f"成功: {success_count}")
print(f"失败: {len(results) - success_count}")
print(f"总Tokens: {total_tokens}")
