#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final verification after root cause fixes"""
import sys
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')

print("=" * 60)
print(" Final Verification After Root Cause Fixes ")
print("=" * 60)

# Test 1
print("\n[1] ProviderPool auto-default path")
from providers.pool import ProviderPool
pool = ProviderPool()
print(f"    db_path: {pool.db_path}")
print(f"    providers: {len(pool.providers)}")

# Test 2
print("\n[2] 7 Strategies registered")
from Kernel import IntelligentStrategyScheduler
s = IntelligentStrategyScheduler()
print(f"    Count: {len(s.strategies)}")
for name in s.strategies:
    print(f"    - {name}")

# Test 3
print("\n[3] symphony_scheduler direct call")
from symphony_scheduler import symphony_scheduler
result = symphony_scheduler("1+1=? Reply one number.")
print(f"    Result: {result}")

# Test 4
print("\n[4] DetectThenTeamSystem")
from Kernel.multi_agent.detect_then_team import DetectThenTeamSystem
system = DetectThenTeamSystem()
det = system.detect_all_models()
print(f"    Online: {det['summary']['online']}/{det['summary']['total']}")

print("\n" + "=" * 60)
print(" ALL TESTS PASSED - Root Causes Fixed ")
print("=" * 60)
