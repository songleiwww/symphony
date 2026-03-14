# -*- coding: utf-8 -*-
import requests, time
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

url = 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions'
key = '3b922877-3fbe-45d1-a298-53f2231c5224'

# 3 officials
officials = [
    {'name': '沈清弦', 'title': '枢密使', 'model': 'glm-4.7'},
    {'name': '陆念昭', 'title': '少府监', 'model': 'glm-4.7'},
    {'name': '苏云渺', 'title': '工部尚书', 'model': 'glm-4.7'},
]

results = []
for o in officials:
    data = {'model': o['model'], 'messages': [{'role': 'system', 'content': f'你是唐朝官员{o["title"]}，文言文回复'}, {'role': 'user', 'content': '序境内核优化建议，10字内'}], 'max_tokens': 50}
    start = time.time()
    r = requests.post(url, headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}, json=data, timeout=120)
    elapsed = time.time() - start
    if r.status_code == 200:
        usage = r.json().get('usage', {})
        print(f'{o["name"]}: {r.json()["choices"][0]["message"]["content"]} | {usage.get("total_tokens", 0)}tokens | {elapsed:.1f}s')
        results.append({'name': o['name'], 'tokens': usage.get('total_tokens', 0), 'elapsed': elapsed})
    else:
        print(f'{o["name"]}: ERROR {r.status_code}')
print(f'Total: {sum(x["tokens"] for x in results)}tokens')
