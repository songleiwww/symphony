# -*- coding: utf-8 -*-
"""
序境系统 - 第二轮搜索学习
多智能体系统与记忆机制
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
    },
    'NVIDIA': {
        'url': 'https://integrate.api.nvidia.com/v1/chat/completions',
        'key': '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',
    }
}

MODEL_MAP = {
    'glm-4.7': {'火山引擎': 'glm-4.7', 'NVIDIA': 'google/gemma-2-27b-it'},
    'glm-4-flash': {'火山引擎': 'glm-4-flash', 'NVIDIA': 'google/gemma-2-27b-it'},
}

DISPATCH_TEAMS = [
    {'id': 'evolve_004', 'name': '顾清歌', 'title': '翰林学士', 'office': '翰林院', 'model': 'glm-4-flash', 'provider': '火山引擎', 'topic': 'AI记忆系统架构设计'},
    {'id': 'evolve_008', 'name': '林码', 'title': '营造司正', 'office': '工部', 'model': 'glm-4.7', 'provider': '火山引擎', 'topic': 'Agent工作流编排最佳实践'},
    {'id': 'evolve_007', 'name': '叶轻尘', 'title': '行走使', 'office': '门下省', 'model': 'glm-4-flash', 'provider': '火山引擎', 'topic': '2026年AI安全与伦理规范'},
]

def call_model(provider, model, messages, max_tokens=150):
    config = API_CONFIGS[provider]
    actual_model = MODEL_MAP.get(model, {}).get(provider, model)
    
    headers = {"Authorization": f"Bearer {config['key']}", "Content-Type": "application/json"}
    data = {"model": actual_model, "messages": messages, "max_tokens": max_tokens}
    
    start = time.time()
    try:
        resp = requests.post(config['url'], headers=headers, json=data, timeout=90)
        elapsed = time.time() - start
        if resp.status_code == 200:
            result = resp.json()
            usage = result.get('usage', {})
            return {'success': True, 'reply': result['choices'][0]['message']['content'], 'provider': provider, 'model': actual_model, 'elapsed': elapsed, 'tokens': usage.get('total_tokens', 0)}
        return {'success': False, 'error': f"HTTP {resp.status_code}"}
    except Exception as e:
        return {'success': False, 'error': str(e)}

print("=" * 80)
print("【序境调度】第二轮学习 - 记忆系统、工作流、安全")
print("=" * 80)
print()

results = []
total_tokens = 0

for official in DISPATCH_TEAMS:
    print(f"【{official['name']}】({official['office']}) → {official['topic']}")
    
    system_prompt = f"你是唐朝官员{official['title']}，博学多才。用文言文简洁回复。"
    user_prompt = f"请用40字概括2026年{official['topic']}的核心要点。"
    
    result = call_model(official['provider'], official['model'], [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])
    
    if result['success']:
        print(f"  ✓ {result['elapsed']:.1f}s | {result['tokens']}tokens")
        print(f"  → {result['reply']}")
        results.append(result)
        total_tokens += result['tokens']
    else:
        print(f"  ✗ {result.get('error')}")
    print()

print("=" * 80)
print(f"【汇总】成功: {len(results)}/{len(DISPATCH_TEAMS)}人 | Token: {total_tokens}")
print("=" * 80)
for r in results:
    print(f"• {r['reply']}")
