#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境内核深度Debug
Root cause analysis - No bypasses allowed
"""
import sys
import os

SYM_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony'
sys.path.insert(0, SYM_PATH)

print("=" * 70)
print(" 序境内核深度Debug ")
print(" Root Cause Analysis - No Bypasses ")
print("=" * 70)

# ==================== 1. Critical Import Tests ====================
print("\n[1] 核心模块导入测试")

tests = [
    ('symphony_scheduler', 'from symphony_scheduler import symphony_scheduler'),
    ('EvolutionKernel', 'from Kernel import EvolutionKernel'),
    ('IntelligentStrategyScheduler', 'from Kernel import IntelligentStrategyScheduler'),
    ('WisdomEngine', 'from Kernel import WisdomEmergenceEngine'),
    ('AlgorithmCoordinator', 'from Kernel import AdaptiveAlgorithmCoordinator'),
    ('ProviderPool', 'from providers.pool import ProviderPool'),
    ('DualEngineScheduler', 'from strategy.dual_engine_scheduler import DualEngineScheduler'),
    ('CrewOrchestrator', 'from Kernel.multi_agent.multi_agent_orchestrator import CrewOrchestrator'),
    ('DetectThenTeamSystem', 'from Kernel.multi_agent.detect_then_team import DetectThenTeamSystem'),
]

results = {}
for name, cmd in tests:
    try:
        exec(cmd, globals())
        results[name] = 'OK'
        print(f"  [OK] {name}")
    except Exception as e:
        results[name] = f"FAIL: {str(e)[:60]}"
        print(f"  [FAIL] {name}: {str(e)[:60]}")

# ==================== 2. Root Cause Analysis ====================
print("\n[2] 根因分析")

# Check IntelligentStrategyScheduler init issue
print("\n  2.1 IntelligentStrategyScheduler init warning")
try:
    from Kernel import IntelligentStrategyScheduler
    import inspect
    sig = inspect.signature(IntelligentStrategyScheduler.__init__)
    print(f"      Signature: {sig}")
    
    # Check __init__ source for federation parameter
    src = inspect.getsource(IntelligentStrategyScheduler.__init__)
    if 'federation' in src:
        print(f"      [ISSUE] __init__ uses 'federation' parameter")
    else:
        print(f"      [OK] No federation parameter in __init__")
except Exception as e:
    print(f"      ERROR: {e}")

# Check ProviderPool default path issue
print("\n  2.2 ProviderPool default db_path issue")
try:
    from providers.pool import ProviderPool
    import inspect
    sig = inspect.signature(ProviderPool.__init__)
    print(f"      Signature: {sig}")
    
    # Check default value
    default = sig.parameters.get('db_path')
    if default:
        print(f"      Default: {default.default}")
    else:
        print(f"      [ISSUE] No default value for db_path")
except Exception as e:
    print(f"      ERROR: {e}")

# ==================== 3. Strategy Registration ====================
print("\n[3] 策略注册问题")

try:
    from Kernel import IntelligentStrategyScheduler
    s = IntelligentStrategyScheduler()
    
    # Check if strategies are registered
    if hasattr(s, 'strategies') and s.strategies:
        print(f"      Strategies registered: {len(s.strategies)}")
        for name in s.strategies:
            print(f"        - {name}")
    else:
        print(f"      [ISSUE] No strategies registered!")
        print(f"      Available attrs: {[a for a in dir(s) if not a.startswith('_')]}")
        
except Exception as e:
    print(f"      ERROR: {e}")

# ==================== 4. Symphony Scheduler Direct Test ====================
print("\n[4] symphony_scheduler 直接调度测试")

try:
    from symphony_scheduler import symphony_scheduler
    result = symphony_scheduler("Reply with 'OK' in one word", max_tokens=10)
    print(f"      Result: {result}")
except Exception as e:
    print(f"      ERROR: {e}")

# ==================== 5. Final Status ====================
print("\n" + "=" * 70)
print(" Debug Complete ")
print("=" * 70)

fail_count = sum(1 for v in results.values() if 'FAIL' in str(v))
print(f"\nSummary: {len(results) - fail_count}/{len(results)} modules OK")

if fail_count > 0:
    print("\nFailed modules:")
    for name, status in results.items():
        if 'FAIL' in str(status):
            print(f"  - {name}")
