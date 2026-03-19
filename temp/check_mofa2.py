# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
from dynamic_dispatcher import DynamicDispatcher

db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
dd = DynamicDispatcher(db)

# Find models with ModelScope API
print("=== Models with ModelScope API ===")
for m in dd.models:
    url = m.get('url', '')
    if 'modelscope' in url.lower():
        print(f"ID:{m['id']} Name:{m['name']} Provider:{m['provider']}")
        print(f"  URL:{url}")
        print(f"  Key:{m.get('key', '')[:20]}...")

# Also show all providers
print("\n=== All Providers ===")
providers = {}
for m in dd.models:
    p = m.get('provider', 'Unknown')
    if p not in providers:
        providers[p] = []
    providers[p].append(m['name'])

for p, names in providers.items():
    print(f"{p}: {len(names)} models")
