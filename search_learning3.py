# -*- coding: utf-8 -*-
"""
序境系统 - 第三轮搜索学习
使用验证可用的模型
"""
import requests
import time
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_CONFIGS = {
    '火山引擎': {
        'url': 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions',
        'key': '3b922877-3fbe-45d1-a298-53f2231c5224',
    }
}

DISPATCH_TEAMS = [
    {'id': 'evolve_002', 'name': '陆念昭', 'title': '少府监', 'office': '少府监本部', 'model': 'glm-4.7', 'provider': '火山引擎', 'topic': '2026年AI Agent工程化规模化落地'},
    {'id': 'evolve_005', 'name': '顾至尊', 'title': '首辅大学士', 'office': '中书省', 'model': 'glm-4.7', 'provider': '火山引擎', 'topic': 'Agentic Workflow最佳实践'},
]

def call_model(provider, model, messages, max_tokens=150):
    config = API_CONFIGS[provider]
    headers = {"Authorization": f"Bearer {config['key']}", "Content-Type": "application/json"}
    data = {"model": model, "messages": messages, "max_tokens": max_tokens}
    
    start = time.time()
    try:
        resp = requests.post(config['url'], headers=headers, json=data, timeout=90)
        elapsed = time.time() - start
        if resp.status_code == 200:
            result = resp.json()
            usage = result.get('usage', {})
            return {'success': True, 'reply': result['choices'][0]['message']['content'], 'provider': provider, 'model': model, 'elapsed': elapsed, 'tokens': usage.get('total_tokens', 0)}
        return {'success': False, 'error': f"HTTP {resp.status_code}"}
    except Exception as e:
        return {'success': False, 'error': str(e)}

print("=" * 80)
print("【序境调度】第三轮学习 - 工程化、Workflow")
print("=" * 80)
print()

results = []
total_tokens = 0

for official in DISPATCH_TEAMS:
    print(f"【{official['name']}】({official['office']}) → {official['topic']}")
    
    system_prompt = f"你是唐朝官员{official['title']}，洞悉时务。用文言文简洁回复。"
    user_prompt = f"请用40字概括2026年{official['topic']}的核心趋势。"
    
    result = call_model(official['provider'], official['model'], [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])
    
    if result['success']:
        print(f"  ✓ {result['elapsed']:.1f}s | {result['tokens']}tokens")
        print(f"  → {result['reply']}")
        results.append({'official': official, 'result': result})
        total_tokens += result['tokens']
    else:
        print(f"  ✗ {result.get('error')}")
    print()

print("=" * 80)
print(f"【汇总】成功: {len(results)}/{len(DISPATCH_TEAMS)}人 | Token: {total_tokens}")
print("=" * 80)
for r in results:
    print(f"• {r['official']['name']}({r['official']['title']}): {r['result']['reply']}")
