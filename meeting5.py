# -*- coding: utf-8 -*-
import requests, time
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

url = 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions'
key = '3b922877-3fbe-45d1-a298-53f2231c5224'

# 5 officials
officials = [
    {'name': '沈清弦', 'title': '枢密使', 'office': '枢密院', 'duty': '架构设计与安全审查'},
    {'name': '陆念昭', 'title': '少府监', 'office': '少府监本部', 'duty': '总体统筹与调度优化'},
    {'name': '苏云渺', 'title': '工部尚书', 'office': '工部', 'duty': '并发处理与性能优化'},
    {'name': '顾清歌', 'title': '翰林学士', 'office': '翰林院', 'duty': '规则制定与文化传承'},
    {'name': '顾至尊', 'title': '首辅大学士', 'office': '中书省', 'duty': '策略规划与资源协调'},
]

results = []
total_tokens = 0
total_prompt = 0
total_completion = 0

print("=" * 80)
print("【少府监全员会议】序境系统内核完善优化研发计划")
print("调度系统：序境调度引擎")
print("=" * 80)
print()

for o in officials:
    system_prompt = f'你是唐朝官员{o["title"]}，职责{o["duty"]}。文言文简洁回复。'
    user_prompt = f'请为序境系统内核优化提出1-2个具体建议，限15字内。'
    
    data = {'model': 'glm-4.7', 'messages': [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ], 'max_tokens': 80}
    
    start = time.time()
    r = requests.post(url, headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}, json=data, timeout=120)
    elapsed = time.time() - start
    
    if r.status_code == 200:
        result = r.json()
        usage = result.get('usage', {})
        reply = result['choices'][0]['message']['content']
        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)
        total_tok = usage.get('total_tokens', 0)
        
        print(f"【{o['name']}】({o['office']})")
        print(f"  模型: glm-4.7 | 耗时: {elapsed:.1f}秒 | Tokens: {total_tok}")
        print(f"  → {reply}")
        print()
        
        results.append({
            'name': o['name'],
            'title': o['title'],
            'office': o['office'],
            'duty': o['duty'],
            'tokens': total_tok,
            'prompt': prompt_tokens,
            'completion': completion_tokens,
            'elapsed': elapsed,
            'reply': reply
        })
        total_tokens += total_tok
        total_prompt += prompt_tokens
        total_completion += completion_tokens
    else:
        print(f"【{o['name']}】ERROR: {r.status_code}")
        print()

# 汇总
print("=" * 80)
print("【会议汇总】序境系统内核完善优化研发计划")
print("=" * 80)
print(f"参会: {len(results)}/{len(officials)}人 | 总Token: {total_tokens}")
print(f"  - Prompt: {total_prompt}")
print(f"  - Completion: {total_completion}")
print()

print("| # | 官员 | 官职 | 官署 | Tokens |")
print("|---|------|------|------|--------|")
for i, r in enumerate(results):
    print(f"| {i+1} | {r['name']} | {r['title']} | {r['office']} | {r['tokens']} |")

print()
print("【研发建议汇总】")
print("=" * 80)
for r in results:
    print(f"• {r['name']}({r['title']}): {r['reply']}")

print()
print(f"总Token消耗: {total_tokens}")
