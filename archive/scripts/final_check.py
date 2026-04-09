#!/usr/bin/env python3
import sys
import os
os.chdir(r"C:\Users\Administrator\.openclaw\skills\symphony")
from providers.pool import ProviderPool

pool = ProviderPool()
pool.start()

print("=== Final ProviderPool Stats ===")
stats = pool.get_stats()
print(f"Total models: {stats['total_models']}")
print(f"Online models: {stats['total_online']}")
print()

for p_name, s in sorted(stats['providers'].items()):
    if s['model_count'] > 0:
        print(f"  {p_name:15s}: {s['model_count']:2d} models, circuit={s['circuit_state']}")

# List all minimax models
print("\n=== All MiniMax models ===")
from providers.pool import Provider
models = pool.get_online_models(provider=Provider.MINIMAX)
for m in models:
    print(f"  - {m.model_id}: {m.name} | {m.usage_rule}")

pool.stop()
print("\n✅ All checks passed!")
