# -*- coding: utf-8 -*-
import requests, time
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

url = 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions'
key = '3b922877-3fbe-45d1-a298-53f2231c5224'

# 3 officials - continued learning
officials = [
    {'name': '顾清歌', 'title': '翰林学士', 'office': '翰林院', 'duty': '规则制定与文化传承'},
    {'name': '顾至尊', 'title': '首辅大学士', 'office': '中书省', 'duty': '策略规划与资源协调'},
    {'name': '沈星衍', 'title': '智囊博士', 'office': '枢密院', 'duty': '策略规划与AI趋势分析'},
]

results = []
total_tokens = 0

print("=" * 80)
print("序境调度 - 第五轮学习 - 2026年AI Agent技术趋势")
print("=" * 80)
print()

for o in officials:
    system_prompt = f'你是唐朝官员{o["title"]}，博学多才，洞悉时务。用文言文简洁回复。'
    user_prompt = f'请用30字概括2026年AI Agent核心技术发展方向。'
    
    data = {'model': 'glm-4.7', 'messages': [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ], 'max_tokens': 100}
    
    start = time.time()
    r = requests.post(url, headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}, json=data, timeout=120)
    elapsed = time.time() - start
    
    if r.status_code == 200:
        result = r.json()
        usage = result.get('usage', {})
        reply = result['choices'][0]['message']['content']
        total_tok = usage.get('total_tokens', 0)
        
        print(f"【{o['name']}】({o['office']})")
        print(f"  模型: glm-4.7 | 耗时: {elapsed:.1f}秒 | Tokens: {total_tok}")
        print(f"  → {reply}")
        print()
        
        results.append({
            'name': o['name'],
            'title': o['title'],
            'office': o['office'],
            'tokens': total_tok,
            'elapsed': elapsed,
            'reply': reply
        })
        total_tokens += total_tok
    else:
        print(f"【{o['name']}】ERROR: {r.status_code}")
        print()

print("=" * 80)
print(f"【汇总】成功: {len(results)}/{len(officials)}人 | Token: {total_tokens}")
print("=" * 80)
for r in results:
    print(f"• {r['name']}({r['title']}): {r['reply']}")
