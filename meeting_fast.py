# -*- coding: utf-8 -*-
"""
序境系统 - 少府监全员开会（精简版）
序境系统内核完善优化研发计划
"""
import requests
import time
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_CONFIG = {
    'url': 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions',
    'key': '3b922877-3fbe-45d1-a298-53f2231c5224',
}

# 核心官属 - 精简到8人
OFFICIALS = [
    {'id': 'evolve_001', 'name': '沈清弦', 'title': '枢密使', 'office': '枢密院', 'duty': '架构设计与安全审查', 'model': 'glm-4.7'},
    {'id': 'evolve_002', 'name': '陆念昭', 'title': '少府监', 'office': '少府监本部', 'duty': '总体统筹与调度优化', 'model': 'glm-4.7'},
    {'id': 'evolve_003', 'name': '苏云渺', 'title': '工部尚书', 'office': '工部', 'duty': '并发处理与性能优化', 'model': 'glm-4.7'},
    {'id': 'evolve_004', 'name': '顾清歌', 'title': '翰林学士', 'office': '翰林院', 'duty': '规则制定与文化传承', 'model': 'glm-4.7'},
    {'id': 'evolve_005', 'name': '顾至尊', 'title': '首辅大学士', 'office': '中书省', 'duty': '策略规划与资源协调', 'model': 'glm-4.7'},
    {'id': 'evolve_006', 'name': '沈星衍', 'title': '智囊博士', 'office': '枢密院', 'duty': '策略规划与意图理解', 'model': 'glm-4.7'},
    {'id': 'evolve_007', 'name': '叶轻尘', 'title': '行走使', 'office': '门下省', 'duty': '执行协调与信息传递', 'model': 'glm-4.7'},
    {'id': 'evolve_008', 'name': '林码', 'title': '营造司正', 'office': '工部', 'duty': 'GPU加速与工程实现', 'model': 'glm-4.7'},
]

def call_model(messages, model='glm-4.7', max_tokens=120):
    headers = {"Authorization": f"Bearer {API_CONFIG['key']}", "Content-Type": "application/json"}
    data = {"model": model, "messages": messages, "max_tokens": max_tokens}
    
    start = time.time()
    try:
        resp = requests.post(API_CONFIG['url'], headers=headers, json=data, timeout=120)
        elapsed = time.time() - start
        
        if resp.status_code == 200:
            result = resp.json()
            usage = result.get('usage', {})
            return {
                'success': True,
                'reply': result['choices'][0]['message']['content'],
                'model': model,
                'elapsed': elapsed,
                'tokens': usage.get('total_tokens', 0)
            }
        return {'success': False, 'error': f"HTTP {resp.status_code}", 'model': model}
    except Exception as e:
        return {'success': False, 'error': str(e), 'model': model}

print("=" * 80)
print("【少府监全员会议】序境系统内核完善优化研发计划")
print("调度系统：序境调度引擎 | 会议主题：提升序境系统内核")
print("=" * 80)
print()

results = []
total_tokens = 0

for i, official in enumerate(OFFICIALS):
    print(f"[{i+1}/{len(OFFICIALS)}] 【{official['name']}】({official['office']}) → {official['duty']}")
    
    system_prompt = f"你是唐朝官员{official['title']}，职责{official['duty']}。请用文言文简洁回复。"
    user_prompt = f"请为序境系统内核优化提出1-2个具体建议，限20字内。"
    
    result = call_model([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])
    
    if result['success']:
        print(f"  ✓ {result['model']} | {result['elapsed']:.1f}s | {result['tokens']}tokens")
        print(f"  → {result['reply']}")
        results.append({'official': official, 'result': result})
        total_tokens += result['tokens']
    else:
        print(f"  ✗ {result.get('error')}")
    print()

# 汇总
print("=" * 80)
print("【会议汇总】序境系统内核完善优化研发计划")
print("=" * 80)
print(f"参会: {len(results)}/{len(OFFICIALS)}人 | 总Token: {total_tokens}")
print()

print("| # | 官员 | 官职 | 官署 | 话题 | Tokens | 耗时 |")
print("|---|------|------|------|------|--------|------|")
for i, r in enumerate(results):
    o = r['official']
    res = r['result']
    print(f"| {i+1} | {o['name']} | {o['title']} | {o['office']} | {o['duty']} | {res['tokens']} | {res['elapsed']:.1f}s |")

print()
print("【研发建议汇总】")
print("=" * 80)
for r in results:
    o = r['official']
    reply = r['result']['reply']
    print(f"• {o['name']}({o['title']}): {reply}")

print()
print(f"总Token消耗: {total_tokens}")
