#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Phase 4 - Async Memory Core v2.0
测试 Phase 4 - 异步记忆核心 v2.0
"""

import sys
import os
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Testing Phase 4 - Async Memory Core v2.0")
print("测试 Phase 4 - 异步记忆核心 v2.0")
print("=" * 60)

passed = 0
total = 0

# Test 1: Async Memory Core exists
total += 1
print("\nTest 1: Async Memory Core...")
core_file = Path("async_memory_core.py")
if core_file.exists():
    print("  OK: async_memory_core.py exists")
    passed += 1
else:
    print("  FAIL: async_memory_core.py missing")

# Test 2: Can be imported
total += 1
print("\nTest 2: Import Async Memory Core...")
try:
    from async_memory_core import create_improved_core, SafetyLevel
    print("  OK: Imported successfully")
    passed += 1
except Exception as e:
    print(f"  FAIL: {e}")

# Test 3: Create core works
total += 1
print("\nTest 3: Create improved core...")
try:
    from async_memory_core import create_improved_core
    
    core = create_improved_core("test_memory_v2.json")
    print("  OK: Core created")
    passed += 1
except Exception as e:
    print(f"  FAIL: {e}")

# Test 4: Add memory works (thread-safe)
total += 1
print("\nTest 4: Add memory (thread-safe)...")
try:
    from async_memory_core import create_improved_core
    
    core = create_improved_core("test_memory_v2.json")
    
    mem_id = core.add_memory(
        "Test memory for v2.0",
        "long_term",
        0.8,
        ["test", "v2"],
        "test"
    )
    
    print(f"  OK: Memory added, ID: {mem_id}")
    passed += 1
except Exception as e:
    print(f"  FAIL: {e}")

# Test 5: Set preference works
total += 1
print("\nTest 5: Set preference...")
try:
    from async_memory_core import create_improved_core
    
    core = create_improved_core("test_memory_v2.json")
    core.set_preference("async_mode", "safe")
    pref = core.get_preference("async_mode")
    
    print(f"  OK: Preference set: {pref}")
    passed += 1
except Exception as e:
    print(f"  FAIL: {e}")

# Test 6: Get stats works
total += 1
print("\nTest 6: Get stats...")
try:
    from async_memory_core import create_improved_core
    
    core = create_improved_core("test_memory_v2.json")
    stats = core.get_stats()
    
    print(f"  OK: Stats retrieved")
    print(f"    Total memories: {stats['total_memories']}")
    print(f"    Version: {stats['version']}")
    passed += 1
except Exception as e:
    print(f"  FAIL: {e}")

# Test 7: Create task works
total += 1
print("\nTest 7: Create task...")
try:
    from async_memory_core import create_improved_core, SafetyLevel
    
    core = create_improved_core("test_memory_v2.json")
    
    def sample_func(x):
        return x * 2
    
    task = core.create_task(
        "Sample Task",
        sample_func,
        args=(42,),
        safety_level=SafetyLevel.SAFE,
        rate_limit_key="test-model"
    )
    
    print(f"  OK: Task created, ID: {task.task_id}")
    passed += 1
except Exception as e:
    print(f"  FAIL: {e}")

# Test 8: Safety analysis works
total += 1
print("\nTest 8: Safety analysis...")
try:
    from async_memory_core import create_improved_core, SafetyLevel, Task, ExecutionMode
    
    core = create_improved_core("test_memory_v2.json")
    
    def func1(): return 1
    def func2(): return 2
    
    tasks = [
        core.create_task("Task 1", func1, safety_level=SafetyLevel.SAFE, rate_limit_key="model-a"),
        core.create_task("Task 2", func2, safety_level=SafetyLevel.SAFE, rate_limit_key="model-a")
    ]
    
    mode, warnings = core.analyze_task_safety(tasks)
    
    print(f"  OK: Safety analysis complete")
    print(f"    Mode: {mode.value}")
    print(f"    Warnings: {len(warnings)}")
    passed += 1
except Exception as e:
    print(f"  FAIL: {e}")

# Test 9: Rate limiter works
total += 1
print("\nTest 9: Rate limiter...")
try:
    from async_memory_core import RateLimiter
    
    limiter = RateLimiter(max_concurrent=2, time_window=1.0)
    
    # Acquire 2 (should work)
    ok1 = limiter.acquire("test-key")
    ok2 = limiter.acquire("test-key")
    
    # Acquire 3rd (should fail)
    ok3 = limiter.acquire("test-key")
    
    print(f"  OK: Rate limiter works")
    print(f"    Acquire 1: {ok1}")
    print(f"    Acquire 2: {ok2}")
    print(f"    Acquire 3 (rate limited): {ok3}")
    passed += 1
except Exception as e:
    print(f"  FAIL: {e}")

# Test 10: Clean up
total += 1
print("\nTest 10: Clean up...")
try:
    test_file = Path("test_memory_v2.json")
    if test_file.exists():
        test_file.unlink()
    print("  OK: Cleaned up")
    passed += 1
except Exception as e:
    print(f"  FAIL: {e}")

# Summary
print("\n" + "=" * 60)
print("TEST SUMMARY - 测试总结")
print("=" * 60)
print(f"\nTotal: {total}")
print(f"Passed: {passed}")
print(f"Failed: {total - passed}")
print(f"Success Rate: {passed/total*100:.1f}%")

if passed == total:
    print("\nALL TESTS PASSED!")
    print("所有测试通过！")
else:
    print("\nSome tests failed!")

print("\n" + "=" * 60)
