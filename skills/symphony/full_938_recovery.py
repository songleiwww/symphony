#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境938模型全量恢复调度
全面测试所有服务商全部模型，建立完整调度能力矩阵
"""
import sys
import sqlite3
import json
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
RESULT_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\full_938_recovery_report.json'

def get_all_models():
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

def test_model(provider_code, provider_config, model_id, model_type, prompt="Reply with exactly 'OK'"):
    import requests
    try:
        url = f"{provider_config['base_url'].replace('/api/v1', '/compatible-mode/v1')}/chat/completions"
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 10,
            "temperature": 0.1
        }
        headers = {"Authorization": f"Bearer {provider_config['api_key']}", "Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        latency = response.elapsed.total_seconds() * 1000
        if response.status_code == 200:
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            return {'success': True, 'response': content[:50], 'latency_ms': round(latency, 1)}
        else:
            return {'success': False, 'error': f"HTTP {response.status_code}"}
    except Exception as e:
        return {'success': False, 'error': str(e)[:80]}

def test_provider_models(provider_code, models, provider_config):
    """测试单个服务商所有模型"""
    provider_models = [m for m in models if m['provider'] == provider_code]
    results = {
        'provider': provider_code,
        'total_models': len(provider_models),
        'tested': [],
        'success_count': 0,
        'fail_count': 0,
        'by_type': {},
        'best_by_type': {}
    }
    
    # 按类型分组测试
    types_to_test = ['text', 'chat', 'multimodal', 'code']
    
    for model_type in types_to_test:
        type_models = [m for m in provider_models if m['model_type'] == model_type]
        if not type_models:
            continue
        
        results['by_type'][model_type] = {'total': len(type_models), 'success': 0, 'fail': 0}
        
        for model in type_models:
            test_result = test_model(provider_code, provider_config, model['model_id'], model['model_type'])
            results['tested'].append({
                'model_id': model['model_id'],
                'model_name': model['model_name'],
                'model_type': model['model_type'],
                'context_window': model['context_window'],
                **test_result
            })
            
            if test_result['success']:
                results['success_count'] += 1
                results['by_type'][model_type]['success'] += 1
            else:
                results['fail_count'] += 1
                results['by_type'][model_type]['fail'] += 1
        
        # 记录该类型最佳模型
        successes = [t for t in results['tested'] if t['model_type'] == model_type and t['success']]
        if successes:
            best = min(successes, key=lambda x: x['latency_ms'])
            results['best_by_type'][model_type] = {
                'model_id': best['model_id'],
                'latency_ms': best['latency_ms']
            }
    
    return results

def main():
    print("=" * 70)
    print(" 序境938模型全量恢复调度 - 深度分析测试 ")
    print("=" * 70)
    
    # 1. 获取所有模型
    print("\n[1/4] 获取所有模型...")
    models = get_all_models()
    print(f"  总计: {len(models)} 个模型")
    
    providers = get_provider_config()
    print(f"  服务商: {list(providers.keys())}")
    
    # 2. 统计模型分布
    print("\n[2/4] 分析模型分布...")
    by_provider = {}
    for m in models:
        p = m['provider']
        if p not in by_provider:
            by_provider[p] = {'total': 0, 'by_type': {}}
        by_provider[p]['total'] += 1
        t = m['model_type']
        if t not in by_provider[p]['by_type']:
            by_provider[p]['by_type'][t] = 0
        by_provider[p]['by_type'][t] = by_provider[p]['by_type'].get(t, 0) + 1
    
    for p, data in by_provider.items():
        print(f"  {p}: {data['total']} 模型")
        for t, c in data['by_type'].items():
            print(f"    - {t}: {c}")
    
    # 3. 全量并行测试
    print("\n[3/4] 全量938模型深度测试...")
    start_time = time.time()
    
    all_results = {
        'total_models': len(models),
        'providers': {},
        'summary': {
            'total_success': 0,
            'total_fail': 0,
            'by_type': {},
            'best_overall': None
        }
    }
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {}
        for provider_code in ['aliyun', 'minimax', 'zhipu', 'nvidia']:
            if provider_code in providers and provider_code in by_provider:
                future = executor.submit(
                    test_provider_models,
                    provider_code,
                    models,
                    providers[provider_code]
                )
                futures[future] = provider_code
        
        for future in as_completed(futures):
            provider_code = futures[future]
            try:
                result = future.result()
                all_results['providers'][provider_code] = result
                
                # 更新全局统计
                all_results['summary']['total_success'] += result['success_count']
                all_results['summary']['total_fail'] += result['fail_count']
                
                # 按类型统计
                for model_type, type_data in result['by_type'].items():
                    if model_type not in all_results['summary']['by_type']:
                        all_results['summary']['by_type'][model_type] = {'success': 0, 'fail': 0}
                    all_results['summary']['by_type'][model_type]['success'] += type_data['success']
                    all_results['summary']['by_type'][model_type]['fail'] += type_data['fail']
                
                print(f"  [{provider_code}] 完成: {result['success_count']}/{result['total_models']} 成功")
            
            except Exception as e:
                print(f"  [{provider_code}] 错误: {str(e)[:50]}")
    
    elapsed = time.time() - start_time
    
    # 4. 找全局最佳
    all_successes = []
    for p_data in all_results['providers'].values():
        for t in p_data['tested']:
            if t.get('success'):
                all_successes.append(t)
    
    if all_successes:
        best_overall = min(all_successes, key=lambda x: x['latency_ms'])
        all_results['summary']['best_overall'] = {
            'model_id': best_overall['model_id'],
            'provider': best_overall.get('provider', 'unknown'),
            'latency_ms': best_overall['latency_ms']
        }
    
    # 5. 保存报告
    print("\n[4/4] 生成完整报告...")
    all_results['generated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
    all_results['elapsed_seconds'] = round(elapsed, 1)
    all_results['kernel_version'] = '4.5.0'
    
    with open(RESULT_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    # 6. 打印摘要
    print("\n" + "=" * 70)
    print(" 序境938模型全量恢复完成 ")
    print("=" * 70)
    print(f"\n总模型数: {all_results['total_models']}")
    print(f"测试成功: {all_results['summary']['total_success']}")
    print(f"测试失败: {all_results['summary']['total_fail']}")
    print(f"成功率: {all_results['summary']['total_success']/max(1, all_results['summary']['total_success']+all_results['summary']['total_fail'])*100:.1f}%")
    print(f"耗时: {elapsed:.1f}秒")
    
    if all_results['summary']['best_overall']:
        bo = all_results['summary']['best_overall']
        print(f"\n🏆 全场最佳: {bo['model_id']}")
        print(f"   服务商: {bo['provider']}")
        print(f"   延迟: {bo['latency_ms']}ms")
    
    print(f"\n详细报告: {RESULT_PATH}")
    
    # 按类型打印最佳
    print("\n各类型最佳模型:")
    for provider_code, p_data in all_results['providers'].items():
        for model_type, best in p_data.get('best_by_type', {}).items():
            print(f"  [{provider_code}] {model_type}: {best['model_id']} ({best['latency_ms']}ms)")
    
    return all_results

if __name__ == '__main__':
    main()
