# -*- coding: utf-8 -*-
import json

with open(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\temp\model_status.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== 魔搭 Models ===')
for m in data.get('在线模型', []):
    if m.get('服务商') == '魔搭':
        print(f"ID:{m.get('id')} Name:{m.get('模型名称')} Provider:{m.get('服务商')} URL:{m.get('API地址')}")

# Count all providers
from collections import Counter
providers = Counter()
for m in data.get('在线模型', []):
    providers[m.get('服务商', 'Unknown')] += 1

print('\n=== All Providers ===')
for p, c in providers.most_common():
    print(f'{p}: {c}')
