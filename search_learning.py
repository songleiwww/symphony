# -*- coding: utf-8 -*-
"""
序境系统 - 少府监官属搜索学习
使用真实模型进行搜索调研
"""
import requests
import time
import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API配置 - 验证可用的模型
API_CONFIGS = {
    '火山引擎': {
        'url': 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions',
        'key': '3b922877-3fbe-45d1-a298-53f2231c5224',
    },
    'NVIDIA': {
        'url': 'https://integrate.api.nvidia.com/v1/chat/completions',
        'key': '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',
    }
}

# 可用模型映射
MODEL_MAP = {
    'glm-4.7': {'火山引擎': 'glm-4.7', 'NVIDIA': 'meta/llama-3.1-70b-instruct'},
    'glm-4-flash': {'火山引擎': 'glm-4-flash', 'NVIDIA': 'meta/llama-3.1-70b-instruct'},
    'Qwen2.5-14B': {'火山引擎': 'glm-4.7', 'NVIDIA': 'google/gemma-2-27b-it', '硅基流动': 'Qwen/Qwen2.5-14B-Instruct'}
}

# 调度官属列表 - 每组3人，不同模型
DISPATCH_TEAMS = [
    # 第一组：枢密院 + 工部
    {'id': 'evolve_001', 'name': '沈清弦', 'title': '枢密使', 'office': '枢密院', 'model': 'glm-4.7', 'provider': '火山引擎', 'topic': 'AI Agent自进化技术架构2026'},
    {'id': 'evolve_003', 'name': '苏云渺', 'title': '工部尚书', 'office': '工部', 'model': 'glm-4.7', 'provider': '火山引擎', 'topic': '多智能体协作框架最新进展'},
    {'id': 'evolve_006', 'name': '沈星衍', 'title': '智囊博士', 'office': '枢密院', 'model': 'Qwen2.5-14B', 'provider': 'NVIDIA', 'topic': 'MCP协议工程化落地'},
]

def call_model(provider, model, messages, max_tokens=200):
    """调用模型API"""
    if provider not in API_CONFIGS:
        return {'success': False, 'error': f'Unknown provider: {provider}'}
    
    config = API_CONFIGS[provider]
    url = config['url']
    api_key = config['key']
    actual_model = MODEL_MAP.get(model, {}).get(provider, model)
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": actual_model, "messages": messages, "max_tokens": max_tokens}
    
    start = time.time()
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=90)
        elapsed = time.time() - start
        
        if resp.status_code == 200:
            result = resp.json()
            usage = result.get('usage', {})
            return {
                'success': True,
                'reply': result['choices'][0]['message']['content'],
                'provider': provider,
                'model': actual_model,
                'elapsed': elapsed,
                'tokens': {
                    'prompt': usage.get('prompt_tokens', 0),
                    'completion': usage.get('completion_tokens', 0),
                    'total': usage.get('total_tokens', 0)
                }
            }
        else:
            return {'success': False, 'error': f"HTTP {resp.status_code}", 'provider': provider, 'detail': resp.text[:100]}
    except Exception as e:
        return {'success': False, 'error': str(e), 'provider': provider}

def run_search():
    print("=" * 80)
    print("【序境调度】少府监官属搜索学习 - AI Agent自进化技术")
    print("=" * 80)
    print()
    
    results = []
    total_tokens = 0
    
    for official in DISPATCH_TEAMS:
        print(f"【{official['name']}】({official['office']}) → {official['topic']}")
        print(f"  模型: {official['provider']}/{official['model']}")
        
        # 文言文风格的system prompt
        system_prompt = f"你是唐朝官员{official['title']}，博学多才，洞悉时务。用文言文回复。"
        user_prompt = f"请搜索并总结2026年AI Agent自进化技术最新进展，重点包括：\n1. 核心技术趋势\n2. 工程化落地情况\n3. 多智能体协作\n4. 安全可靠性\n\n请用简洁文言文概括，限80字内。"
        
        result = call_model(official['provider'], official['model'], [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        if result['success']:
            print(f"  ✓ 成功 | {result['elapsed']:.1f}秒 | {result['tokens']['total']}tokens")
            print(f"  → {result['reply']}")
            results.append({'official': official, 'result': result})
            total_tokens += result['tokens']['total']
        else:
            print(f"  ✗ 失败: {result.get('error')}")
            # 尝试备用
            print(f"  → 尝试备用...")
            for alt_provider in ['火山引擎', 'NVIDIA']:
                if alt_provider != official['provider']:
                    result = call_model(alt_provider, official['model'], [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ])
                    if result['success']:
                        print(f"  ✓ 备用成功 | {alt_provider}")
                        results.append({'official': official, 'result': result})
                        total_tokens += result['tokens']['total']
                        break
        print()
    
    # 汇总
    print("=" * 80)
    print("【搜索汇总】")
    print("=" * 80)
    print(f"成功: {len(results)}/{len(DISPATCH_TEAMS)}人 | 总Token: {total_tokens}")
    print()
    
    for r in results:
        o = r['official']
        res = r['result']
        print(f"• {o['name']}({o['title']}): {res['reply'][:60]}...")
    
    return results

if __name__ == "__main__":
    run_search()
