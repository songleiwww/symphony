#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test v0.4.0 Phase 3 - 测试v0.4.0 Phase 3功能
"""

import sys
import os
import asyncio
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Test v0.4.0 Phase 3")
print("=" * 60)

passed = 0
total = 0

# Test 1: Async Task Queue
total += 1
print(f"\n[Test {total}] Async Task Queue...")
try:
    from async_task_queue import create_async_task_queue
    queue = create_async_task_queue()
    print("  OK: Async task queue created")
    passed += 1
except Exception as e:
    print(f"  FAIL: {e}")

# Test 2: Concurrency Monitor
total += 1
print(f"\n[Test {total}] Concurrency Monitor...")
try:
    from concurrency_monitor import create_concurrency_monitor
    monitor = create_concurrency_monitor()
    print("  OK: Concurrency monitor created")
    passed += 1
except Exception as e:
    print(f"  FAIL: {e}")

# Test 3: Queue create task
total += 1
print(f"\n[Test {total}] Queue create task...")
try:
    from async_task_queue import create_async_task_queue, TaskPriority
    
    def sample_func(x):
        return x * 2
    
    queue = create_async_task_queue()
    task_id = queue.create_task("Sample", sample_func, args=(42,), priority=TaskPriority.NORMAL)
    print(f"  OK: Task created, ID: {task_id}")
    passed += 1
except Exception as e:
    print(f"  FAIL: {e}")

# Test 4: Monitor task tracking
total += 1
print(f"\n[Test {total}] Monitor task tracking...")
try:
    from concurrency_monitor import create_concurrency_monitor
    
    monitor = create_concurrency_monitor()
    monitor.task_started()
    monitor.task_started()
    monitor.task_completed(0.1)
    monitor.task_completed(0.2)
    
    metrics = monitor.get_current_metrics()
    if metrics["completed_tasks"] == 2:
        print(f"  OK: Task tracking works")
        passed += 1
    else:
        print(f"  FAIL: Task tracking incorrect")
except Exception as e:
    print(f"  FAIL: {e}")

# Test 5: Monitor dashboard
total += 1
print(f"\n[Test {total}] Monitor dashboard...")
try:
    from concurrency_monitor import create_concurrency_monitor
    
    monitor = create_concurrency_monitor()
    dashboard = monitor.get_ascii_dashboard()
    if len(dashboard) > 100:
        print(f"  OK: Dashboard generated")
        passed += 1
    else:
        print(f"  FAIL: Dashboard too short")
except Exception as e:
    print(f"  FAIL: {e}")

# Summary
print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print(f"\nTotal: {total}")
print(f"Passed: {passed}")
print(f"Failed: {total - passed}")
print(f"Success Rate: {passed/total*100:.1f}%")

if passed == total:
    print("\nALL TESTS PASSED!")
else:
    print("\nSome tests failed!")

print("\n" + "=" * 60)
