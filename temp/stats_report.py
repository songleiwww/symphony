# -*- coding: utf-8 -*-
import json
from collections import Counter

with open(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\temp\model_status.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

models = data.get('在线模型', [])

# Count by provider
providers = Counter()
for m in models:
    providers[m.get('服务商', 'Unknown')] += 1

print('=== Service Provider Stats ===')
for p, c in providers.most_common():
    print(f'{p}: {c}')

print('\n=== Total Models ===')
print(f'Online: {len(models)}')

# List top models
print('\n=== Top Models by Provider ===')
for m in models[:10]:
    print(f"ID:{m.get('id')} Provider:{m.get('服务商')} Name:{m.get('模型名称')}")
