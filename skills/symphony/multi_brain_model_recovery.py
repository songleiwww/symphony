#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境巅峰调度恢复 - 多脑分析调度所有可用模型
使用多智能体编排并行分析938+模型，恢复完整调度能力
"""
import sys
import sqlite3
import json
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
RESULT_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\model_analysis_report.json'

def get_all_models():
    """从数据库获取所有可用模型"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT provider, model_id, model_name, model_type, context_window, max_tokens, is_free, is_enabled
        FROM model_config WHERE is_enabled = 1
    """)
    models = []
    for row in cursor.fetchall():
        models.append({
            'provider': row[0],
            'model_id': row[1],
            'model_name': row[2],
            'model_type': row[3],
            'context_window': row[4],
            'max_tokens': row[5],
            'is_free': bool(row[6]),
            'is_enabled': bool(row[7])
        })
    conn.close()
    return models

def get_provider_config():
    """获取服务商配置"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT provider_code, provider_name, base_url, api_key FROM provider_registry WHERE is_enabled = 1")
    providers = {}
    for row in cursor.fetchall():
        providers[row[0]] = {
            'name': row[1],
            'base_url': row[2].rstrip('/'),
            'api_key': row[3]
        }
    conn.close()
    return providers

def test_model(provider_code, provider_config, model_id, prompt="Say 'OK' in exactly one word."):
    """测试单个模型"""
    import requests
    try:
        url = f"{provider_config['base_url'].replace('/api/v1', '/compatible-mode/v1')}/chat/completions"
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 20,
            "temperature": 0.7
        }
        headers = {"Authorization": f"Bearer {provider_config['api_key']}", "Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            return {'success': True, 'response': content, 'latency_ms': response.elapsed.total_seconds() * 1000}
        else:
            return {'success': False, 'error': f"HTTP {response.status_code}"}
    except Exception as e:
        return {'success': False, 'error': str(e)[:100]}

def analyze_by_provider(provider_code, models, provider_config, max_test=5):
    """分析单个服务商的模型"""
    text_models = [m for m in models if m['provider'] == provider_code and m['model_type'] in ('text', 'chat')]
    results = {
        'provider': provider_code,
        'total_models': len(text_models),
        'tested_count': 0,
        'success_count': 0,
        'failed_count': 0,
        'best_model': None,
        'tested_models': []
    }
    
    # 测试前5个模型
    for model in text_models[:max_test]:
        print(f"  [{provider_code}] Testing {model['model_id'][:40]}...")
        test_result = test_model(provider_code, provider_config, model['model_id'])
        results['tested_count'] += 1
        if test_result['success']:
            results['success_count'] += 1
            results['tested_models'].append({
                'model_id': model['model_id'],
                'model_name': model['model_name'],
                'context_window': model['context_window'],
                'response': test_result['response'],
                'latency_ms': round(test_result['latency_ms'], 1)
            })
            if not results['best_model'] or test_result['latency_ms'] < results['best_model'].get('latency_ms', 9999):
                results['best_model'] = results['tested_models'][-1]
        else:
            results['failed_count'] += 1
            results['tested_models'].append({
                'model_id': model['model_id'],
                'error': test_result['error']
            })
    
    return results

def main():
    print("=" * 60)
    print("序境巅峰调度恢复 - 多脑分析所有可用模型")
    print("=" * 60)
    
    # 1. 获取所有模型
    print("\n[1/4] 获取所有可用模型...")
    models = get_all_models()
    print(f"  总计: {len(models)} 个模型")
    
    by_provider = {}
    for m in models:
        p = m['provider']
        if p not in by_provider:
            by_provider[p] = []
        by_provider[p].append(m)
    for p, ms in by_provider.items():
        print(f"  {p}: {len(ms)} 个模型")
    
    # 2. 获取服务商配置
    print("\n[2/4] 获取服务商配置...")
    providers = get_provider_config()
    print(f"  {len(providers)} 个服务商已配置")
    
    # 3. 多脑并行分析
    print("\n[3/4] 多脑并行分析各服务商模型...")
    all_results = {
        'total_models': len(models),
        'providers': {},
        'summary': {
            'total_providers': len(providers),
            'total_tested': 0,
            'total_success': 0,
            'total_failed': 0
        }
    }
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {}
        for provider_code in ['aliyun', 'minimax', 'zhipu', 'nvidia']:
            if provider_code in providers and provider_code in by_provider:
                future = executor.submit(
                    analyze_by_provider,
                    provider_code,
                    models,
                    providers[provider_code],
                    max_test=8  # 每个服务商测8个
                )
                futures[future] = provider_code
        
        for future in as_completed(futures):
            provider_code = futures[future]
            try:
                result = future.result()
                all_results['providers'][provider_code] = result
                all_results['summary']['total_tested'] += result['tested_count']
                all_results['summary']['total_success'] += result['success_count']
                all_results['summary']['total_failed'] += result['failed_count']
                print(f"  [{provider_code}] 完成: {result['success_count']}/{result['tested_count']} 成功")
            except Exception as e:
                print(f"  [{provider_code}] 失败: {e}")
    
    # 4. 生成报告
    print("\n[4/4] 生成分析报告...")
    all_results['generated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
    all_results['kernel_version'] = '4.5.0'
    
    with open(RESULT_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("序境巅峰调度恢复完成")
    print("=" * 60)
    print(f"总计模型: {all_results['total_models']}")
    print(f"测试模型: {all_results['summary']['total_tested']}")
    print(f"成功: {all_results['summary']['total_success']}")
    print(f"失败: {all_results['summary']['total_failed']}")
    print(f"\n详细报告: {RESULT_PATH}")
    
    # 打印最佳模型
    print("\n各服务商最佳模型:")
    for p, data in all_results['providers'].items():
        if data.get('best_model'):
            bm = data['best_model']
            print(f"  {p}: {bm['model_id']} ({bm['latency_ms']}ms)")
    
    return all_results

if __name__ == '__main__':
    main()
