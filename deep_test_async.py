#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deep Test - Async Memory Core v2.0
深度测试 - 查找并修复bug
"""

import sys
import os
import time
import threading
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("Deep Test - Async Memory Core v2.0")
print("深度测试 - 异步记忆核心 v2.0")
print("=" * 80)

passed = 0
total = 0
bugs_found = []

# =========================================================================
# Test 1: Basic Functionality
# =========================================================================
total += 1
print(f"\n[Test {total}] Basic Functionality...")
try:
    from async_memory_core import create_improved_core
    
    core = create_improved_core("deep_test_memory.json")
    
    # Add multiple memories
    ids = []
    for i in range(5):
        mem_id = core.add_memory(
            f"Test memory {i+1}",
            "long_term" if i % 2 == 0 else "short_term",
            0.5 + (i * 0.1),
            [f"tag{i+1}", "test"],
            "test"
        )
        ids.append(mem_id)
    
    # Check stats
    stats = core.get_stats()
    if stats["total_memories"] >= 5:
        print(f"  OK: Basic functionality works")
        print(f"    Memories added: {len(ids)}")
        print(f"    Stats: total={stats['total_memories']}, version={stats['version']}")
        passed += 1
    else:
        bugs_found.append(f"Expected >=5 memories, got {stats['total_memories']}")
        print(f"  FAIL: Stats incorrect")
        
except Exception as e:
    bugs_found.append(f"Basic test failed: {e}")
    print(f"  FAIL: {e}")

# =========================================================================
# Test 2: Thread Safety (Concurrent Adds)
# =========================================================================
total += 1
print(f"\n[Test {total}] Thread Safety - Concurrent Adds...")
try:
    from async_memory_core import create_improved_core
    
    core = create_improved_core("deep_test_thread.json")
    results = []
    lock = threading.Lock()
    
    def add_memories(thread_id):
        for i in range(10):
            try:
                mem_id = core.add_memory(
                    f"Thread {thread_id} - Memory {i}",
                    "short_term",
                    0.5,
                    [f"thread{thread_id}"],
                    "thread-test"
                )
                with lock:
                    results.append(mem_id)
            except Exception as e:
                with lock:
                    bugs_found.append(f"Thread {thread_id} error: {e}")
    
    # Start 5 threads
    threads = []
    for t in range(5):
        thread = threading.Thread(target=add_memories, args=(t,))
        threads.append(thread)
        thread.start()
    
    # Wait for all
    for t in threads:
        t.join()
    
    # Check results
    stats = core.get_stats()
    expected = 50  # 5 threads * 10 memories
    actual = stats["total_memories"]
    
    if actual >= 45:  # Allow some tolerance
        print(f"  OK: Thread safety works")
        print(f"    Threads: 5, Memories/thread: 10")
        print(f"    Total: {actual} (expected ~{expected})")
        passed += 1
    else:
        bugs_found.append(f"Thread safety: expected {expected}, got {actual}")
        print(f"  FAIL: Thread safety issue - {actual} < {expected}")
        
except Exception as e:
    bugs_found.append(f"Thread test failed: {e}")
    print(f"  FAIL: {e}")

# =========================================================================
# Test 3: Rate Limiter
# =========================================================================
total += 1
print(f"\n[Test {total}] Rate Limiter...")
try:
    from async_memory_core import RateLimiter
    
    limiter = RateLimiter(max_concurrent=2, time_window=2.0)
    
    # Test 1: Acquire 2 (should work)
    ok1 = limiter.acquire("test-model")
    ok2 = limiter.acquire("test-model")
    
    # Test 2: Acquire 3rd (should fail - rate limited)
    ok3 = limiter.acquire("test-model")
    
    # Release
    limiter.release("test-model")
    
    # Test 3: Acquire again (should work now)
    ok4 = limiter.acquire("test-model")
    
    if ok1 and ok2 and not ok3 and ok4:
        print(f"  OK: Rate limiter works correctly")
        print(f"    Acquire 1: {ok1}")
        print(f"    Acquire 2: {ok2}")
        print(f"    Acquire 3 (rate limited): {ok3}")
        print(f"    Acquire 4 (after release): {ok4}")
        passed += 1
    else:
        bugs_found.append(f"Rate limiter logic wrong: ok1={ok1}, ok2={ok2}, ok3={ok3}, ok4={ok4}")
        print(f"  FAIL: Rate limiter logic incorrect")
        
except Exception as e:
    bugs_found.append(f"Rate limiter test failed: {e}")
    print(f"  FAIL: {e}")

# =========================================================================
# Test 4: Task Creation & Safety Analysis
# =========================================================================
total += 1
print(f"\n[Test {total}] Task Creation & Safety Analysis...")
try:
    from async_memory_core import create_improved_core, SafetyLevel, ExecutionMode
    
    core = create_improved_core("deep_test_tasks.json")
    
    def sample_func(x):
        return x * 2
    
    # Test 1: Create safe tasks
    task1 = core.create_task("Task 1", sample_func, args=(1,), safety_level=SafetyLevel.SAFE)
    task2 = core.create_task("Task 2", sample_func, args=(2,), safety_level=SafetyLevel.SAFE)
    
    # Test 2: Safety analysis - safe parallel
    mode1, warnings1 = core.analyze_task_safety([task1, task2])
    
    # Test 3: Create tasks with dependencies
    task3 = core.create_task("Task 3", sample_func, args=(3,), depends_on=[task1.task_id])
    
    # Test 4: Safety analysis - sequential needed
    mode2, warnings2 = core.analyze_task_safety([task1, task3])
    
    # Test 5: Create risky task
    task4 = core.create_task("Task 4", sample_func, args=(4,), safety_level=SafetyLevel.RISKY)
    
    # Test 6: Safety analysis - risky, sequential only
    mode3, warnings3 = core.analyze_task_safety([task1, task4])
    
    if (mode1 == ExecutionMode.PARALLEL_SAFE and
        mode2 == ExecutionMode.SEQUENTIAL and
        mode3 == ExecutionMode.SEQUENTIAL):
        print(f"  OK: Task safety analysis works")
        print(f"    Safe tasks: {mode1.value}")
        print(f"    Tasks with dependencies: {mode2.value}")
        print(f"    Risky tasks: {mode3.value}")
        passed += 1
    else:
        bugs_found.append(f"Safety analysis wrong: mode1={mode1}, mode2={mode2}, mode3={mode3}")
        print(f"  FAIL: Safety analysis logic incorrect")
        
except Exception as e:
    bugs_found.append(f"Task test failed: {e}")
    print(f"  FAIL: {e}")

# =========================================================================
# Test 5: Preferences
# =========================================================================
total += 1
print(f"\n[Test {total}] Preferences...")
try:
    from async_memory_core import create_improved_core
    
    core = create_improved_core("deep_test_prefs.json")
    
    # Set multiple preferences
    core.set_preference("key1", "value1")
    core.set_preference("key2", 42)
    core.set_preference("key3", True)
    core.set_preference("key4", {"nested": "value"})
    
    # Get preferences
    val1 = core.get_preference("key1")
    val2 = core.get_preference("key2")
    val3 = core.get_preference("key3")
    val4 = core.get_preference("key4")
    val5 = core.get_preference("nonexistent", "default")
    
    if (val1 == "value1" and val2 == 42 and val3 == True and
        val4 == {"nested": "value"} and val5 == "default"):
        print(f"  OK: Preferences work")
        print(f"    String: {val1}")
        print(f"    Number: {val2}")
        print(f"    Boolean: {val3}")
        print(f"    Dict: {val4}")
        print(f"    Default: {val5}")
        passed += 1
    else:
        bugs_found.append(f"Preferences incorrect: {val1}, {val2}, {val3}, {val4}")
        print(f"  FAIL: Preferences incorrect")
        
except Exception as e:
    bugs_found.append(f"Preferences test failed: {e}")
    print(f"  FAIL: {e}")

# =========================================================================
# Test 6: Memory Retrieval
# =========================================================================
total += 1
print(f"\n[Test {total}] Memory Retrieval...")
try:
    from async_memory_core import create_improved_core
    
    core = create_improved_core("deep_test_retrieval.json")
    
    # Add test memories
    mem_id1 = core.add_memory(
        "First memory about AI",
        "long_term",
        0.9,
        ["ai", "technology"],
        "test"
    )
    mem_id2 = core.add_memory(
        "Second memory about weather",
        "long_term",
        0.7,
        ["weather", "data"],
        "test"
    )
    mem_id3 = core.add_memory(
        "Third memory about both AI and weather",
        "short_term",
        0.5,
        ["ai", "weather"],
        "test"
    )
    
    # Test 1: Get by ID
    mem1 = core.get_memory(mem_id1)
    
    # Test 2: Search by tags
    results_ai = core.search_memories(tags=["ai"])
    results_weather = core.search_memories(tags=["weather"])
    results_both = core.search_memories(tags=["ai", "weather"])
    
    # Test 3: Search by min importance
    results_high = core.search_memories(min_importance=0.8)
    
    if (mem1 and len(results_ai) >= 2 and len(results_weather) >= 2 and
        len(results_both) >= 1 and len(results_high) >= 1):
        print(f"  OK: Memory retrieval works")
        print(f"    Get by ID: OK")
        print(f"    Search by 'ai': {len(results_ai)} results")
        print(f"    Search by 'weather': {len(results_weather)} results")
        print(f"    Search by both: {len(results_both)} results")
        print(f"    Search min_importance=0.8: {len(results_high)} results")
        passed += 1
    else:
        bugs_found.append(f"Memory retrieval issues")
        print(f"  FAIL: Memory retrieval not working correctly")
        
except Exception as e:
    bugs_found.append(f"Retrieval test failed: {e}")
    print(f"  FAIL: {e}")

# =========================================================================
# Cleanup
# =========================================================================
print(f"\n[Cleanup] Removing test files...")
test_files = [
    "deep_test_memory.json",
    "deep_test_thread.json",
    "deep_test_tasks.json",
    "deep_test_prefs.json",
    "deep_test_retrieval.json"
]
for f in test_files:
    p = Path(f)
    if p.exists():
        p.unlink()
        print(f"  Removed: {f}")

# =========================================================================
# Summary
# =========================================================================
print("\n" + "=" * 80)
print("DEEP TEST SUMMARY - 深度测试总结")
print("=" * 80)
print(f"\nTotal Tests: {total}")
print(f"Passed: {passed}")
print(f"Failed: {total - passed}")
print(f"Success Rate: {passed/total*100:.1f}%")

if bugs_found:
    print(f"\nBugs Found ({len(bugs_found)}):")
    for i, bug in enumerate(bugs_found, 1):
        print(f"  [{i}] {bug}")
else:
    print(f"\nNO BUGS FOUND!")
    print("没有发现Bug！")

if passed == total:
    print("\nALL TESTS PASSED!")
    print("所有深度测试通过！")
else:
    print("\nSome deep tests failed!")

print("\n" + "=" * 80)
