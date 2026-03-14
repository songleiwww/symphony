# -*- coding: utf-8 -*-
import requests, time
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

url = 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions'
key = '3b922877-3fbe-45d1-a298-53f2231c5224'

# 3 officials
officials = [
    {'name': '苏云渺', 'title': '工部尚书', 'office': '工部'},
    {'name': '林码', 'title': '营造司正', 'office': '工部'},
    {'name': '叶轻尘', 'title': '行走使', 'office': '门下省'},
]

results = []
total_tokens = 0

print("序境调度 - 第六轮学习")
print("=" * 60)

for o in officials:
    data = {'model': 'glm-4.7', 'messages': [
        {'role': 'system', 'content': f'你是唐朝官员{o["title"]}，文言文简洁回复。'},
        {'role': 'user', 'content': 'AI Agent工程化落地要点，15字内'}
    ], 'max_tokens': 50}
    
    start = time.time()
    try:
        r = requests.post(url, headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}, json=data, timeout=60)
        elapsed = time.time() - start
        
        if r.status_code == 200:
            result = r.json()
            usage = result.get('usage', {})
            reply = result['choices'][0]['message']['content']
            total_tok = usage.get('total_tokens', 0)
            
            print(f"【{o['name']}】{total_tok}tokens | {elapsed:.1f}s → {reply}")
            results.append({'name': o['name'], 'tokens': total_tok, 'reply': reply})
            total_tokens += total_tok
        else:
            print(f"【{o['name']}】ERROR {r.status_code}")
    except Exception as e:
        print(f"【{o['name']}】ERROR: {str(e)[:30]}")

print(f"\n总计: {total_tokens}tokens")
for r in results:
    print(f"• {r['name']}: {r['reply']}")
