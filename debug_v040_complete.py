#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v0.4.0 Complete Debug Test - 交响v0.4.0完整Debug测试
Test all v0.4.0 features thoroughly - 全面测试v0.4.0所有功能
"""

import sys
import os
import asyncio
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("Symphony v0.4.0 Complete Debug Test")
print("交响v0.4.0完整Debug测试")
print("=" * 70)

passed = 0
total = 0
errors = []

# =========================================================================
# Phase 1: Memory Importer/Exporter
# =========================================================================
print("\n[Phase 1] Memory Importer/Exporter - 记忆导入导出")
print("-" * 70)

total += 1
print(f"\n[1.{total}] Test 1: Create importer/exporter...")
try:
    from memory_importer_exporter import create_memory_importer_exporter
    importer = create_memory_importer_exporter()
    print("  OK: Importer/exporter created")
    passed += 1
except Exception as e:
    errors.append(f"Phase 1 Test 1: {e}")
    print(f"  FAIL: {e}")

# =========================================================================
# Phase 2: Context-aware Memory + Streaming Output
# =========================================================================
print("\n[Phase 2] Context-aware Memory + Streaming Output - 情境感知记忆 + 流式输出")
print("-" * 70)

total += 1
print(f"\n[2.{total}] Test 1: Context-aware memory...")
try:
    from context_aware_memory import create_context_aware_memory
    ctx = create_context_aware_memory()
    summary = ctx.get_context_summary()
    if "session" in summary and "time_of_day" in summary["session"]:
        print("  OK: Context-aware memory works")
        passed += 1
    else:
        errors.append(f"Phase 2 Test 1: Context incomplete")
        print("  FAIL: Context incomplete")
except Exception as e:
    errors.append(f"Phase 2 Test 1: {e}")
    print(f"  FAIL: {e}")

total += 1
print(f"\n[2.{total}] Test 2: Streaming output...")
try:
    from streaming_output import create_streaming_output
    stream = create_streaming_output()
    stream.start()
    stream.send_text("Test message")
    stream.finish()
    full_text = stream.get_full_text()
    if "Test" in full_text:
        print("  OK: Streaming output works")
        passed += 1
    else:
        errors.append(f"Phase 2 Test 2: Full text incorrect")
        print("  FAIL: Full text incorrect")
except Exception as e:
    errors.append(f"Phase 2 Test 2: {e}")
    print(f"  FAIL: {e}")

# =========================================================================
# Phase 3: Async Task Queue + Concurrency Monitor
# =========================================================================
print("\n[Phase 3] Async Task Queue + Concurrency Monitor - 异步任务队列 + 并发监控")
print("-" * 70)

total += 1
print(f"\n[3.{total}] Test 1: Async task queue...")
try:
    from async_task_queue import create_async_task_queue, TaskPriority
    
    def sample_func(x):
        return x * 2
    
    queue = create_async_task_queue()
    task_id = queue.create_task("Sample", sample_func, args=(21,), priority=TaskPriority.NORMAL)
    if task_id.startswith("task_"):
        print("  OK: Async task queue works")
        passed += 1
    else:
        errors.append(f"Phase 3 Test 1: Task ID incorrect")
        print("  FAIL: Task ID incorrect")
except Exception as e:
    errors.append(f"Phase 3 Test 1: {e}")
    print(f"  FAIL: {e}")

total += 1
print(f"\n[3.{total}] Test 2: Concurrency monitor...")
try:
    from concurrency_monitor import create_concurrency_monitor
    
    monitor = create_concurrency_monitor()
    monitor.task_started()
    monitor.task_started()
    monitor.task_completed(0.1)
    monitor.task_completed(0.2)
    
    metrics = monitor.get_current_metrics()
    if metrics["completed_tasks"] == 2:
        print("  OK: Concurrency monitor works")
        passed += 1
    else:
        errors.append(f"Phase 3 Test 2: Completed tasks incorrect")
        print("  FAIL: Completed tasks incorrect")
except Exception as e:
    errors.append(f"Phase 3 Test 2: {e}")
    print(f"  FAIL: {e}")

# =========================================================================
# Phase 4: Deadlock Detection + UX Improvements
# =========================================================================
print("\n[Phase 4] Deadlock Detection + UX Improvements - 死锁检测 + 用户体验改进")
print("-" * 70)

total += 1
print(f"\n[4.{total}] Test 1: Deadlock detector...")
try:
    from deadlock_detector import create_deadlock_detector, DeadlockStatus
    
    detector = create_deadlock_detector()
    detector.add_wait("task1", "task2", "resourceA")
    status, cycle = detector.detect_deadlock()
    if status == DeadlockStatus.NO_DEADLOCK:
        print("  OK: Deadlock detector works (no deadlock)")
        passed += 1
    else:
        errors.append(f"Phase 4 Test 1: Unexpected deadlock")
        print("  FAIL: Unexpected deadlock")
except Exception as e:
    errors.append(f"Phase 4 Test 1: {e}")
    print(f"  FAIL: {e}")

total += 1
print(f"\n[4.{total}] Test 2: UX improvements...")
try:
    from ux_improvements import create_ux_improvements, UXMessageType
    
    ux = create_ux_improvements()
    # Just test that methods don't crash
    ux.show_success("Debug test passed")
    ux.show_progress(0.5, "Debug progress")
    print("\n  OK: UX improvements works")
    passed += 1
except Exception as e:
    errors.append(f"Phase 4 Test 2: {e}")
    print(f"  FAIL: {e}")

# =========================================================================
# Summary
# =========================================================================
print("\n" + "=" * 70)
print("DEBUG SUMMARY")
print("=" * 70)
print(f"\nTotal: {total}")
print(f"Passed: {passed}")
print(f"Failed: {total - passed}")
print(f"Success Rate: {passed/total*100:.1f}%")

if errors:
    print("\nErrors:")
    for i, err in enumerate(errors, 1):
        print(f"  {i}. {err}")
else:
    print("\nNo errors!")

if passed == total:
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED! v0.4.0 is working correctly!")
    print("所有测试通过！v0.4.0工作正常！")
    print("=" * 70)
else:
    print("\n" + "=" * 70)
    print("Some tests failed! Please check errors above.")
    print("部分测试失败！请检查上面的错误。")
    print("=" * 70)

print(f"\nFinished at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
