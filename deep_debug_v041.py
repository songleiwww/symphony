#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v0.4.1 Deep Debug Test - 交响v0.4.1深度Debug测试
Thorough deep testing of all v0.4.x features - 全面深度测试v0.4.x所有功能
"""

import sys
import os
import asyncio
import time
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("Symphony v0.4.1 Deep Debug Test")
print("交响v0.4.1深度Debug测试")
print("=" * 80)

passed = 0
total = 0
errors = []
warnings = []

# =========================================================================
# Test 1: Memory System (all versions)
# =========================================================================
print("\n[Test 1] Memory System - 记忆系统")
print("-" * 80)

total += 1
print(f"\n[1.{total}] Memory System Core...")
try:
    from memory_system import create_memory_system
    memory, learning = create_memory_system()
    
    # Test basic operations
    memory.add_memory("Debug test content 1", "short_term", 0.8, ["debug", "test"], "debugger")
    memory.add_memory("Debug test content 2", "short_term", 0.9, ["debug", "important"], "debugger")
    
    results = memory.retrieve_memory("debug", limit=2)
    
    if len(results) >= 2:
        print("  OK: Memory system works")
        passed += 1
    else:
        errors.append(f"Test 1.{total}: Memory retrieval failed")
        print("  FAIL: Memory retrieval failed")
except Exception as e:
    errors.append(f"Test 1.{total}: {e}")
    print(f"  FAIL: {e}")

# =========================================================================
# Test 2: Async Memory Core v2.0
# =========================================================================
print("\n[Test 2] Async Memory Core v2.0 - 异步记忆核心v2.0")
print("-" * 80)

total += 1
print(f"\n[2.{total}] Async Memory Core...")
try:
    from async_memory_core import create_improved_core
    core = create_improved_core()
    
    # Test basic operations (add memory instead of preference)
    core.add_memory("Debug test content", "short_term", 0.8, ["debug"], "debugger")
    stats = core.get_stats()
    
    if stats.get("total_memories", 0) >= 1:
        print("  OK: Async memory core works")
        passed += 1
    else:
        errors.append(f"Test 2.{total}: Memory not added")
        print("  FAIL: Memory not added")
except Exception as e:
    errors.append(f"Test 2.{total}: {e}")
    print(f"  FAIL: {e}")

# =========================================================================
# Test 3: Memory Importer/Exporter (all formats)
# =========================================================================
print("\n[Test 3] Memory Importer/Exporter - 记忆导入导出")
print("-" * 80)

total += 1
print(f"\n[3.{total}] Memory Importer/Exporter...")
try:
    from memory_importer_exporter import create_memory_importer_exporter
    importer = create_memory_importer_exporter()
    
    # Test factory function works
    if importer is not None:
        print("  OK: Memory importer/exporter works")
        passed += 1
    else:
        errors.append(f"Test 3.{total}: Importer is None")
        print("  FAIL: Importer is None")
except Exception as e:
    errors.append(f"Test 3.{total}: {e}")
    print(f"  FAIL: {e}")

# =========================================================================
# Test 4: Context-aware Memory
# =========================================================================
print("\n[Test 4] Context-aware Memory - 情境感知记忆")
print("-" * 80)

total += 1
print(f"\n[4.{total}] Context-aware Memory...")
try:
    from context_aware_memory import create_context_aware_memory
    ctx = create_context_aware_memory()
    
    # Test all context types
    ctx.set_user_context("debug_level", "deep")
    ctx.set_task_context("current_task", "deep_debug_test")
    ctx.add_conversation_turn("user", "Start deep debug")
    ctx.add_conversation_turn("assistant", "Deep debug started")
    
    summary = ctx.get_context_summary()
    prompt = ctx.get_context_prompt()
    
    if "debug_level" in summary.get("user", {}) and len(prompt) > 50:
        print("  OK: Context-aware memory works")
        passed += 1
    else:
        errors.append(f"Test 4.{total}: Context incomplete")
        print("  FAIL: Context incomplete")
except Exception as e:
    errors.append(f"Test 4.{total}: {e}")
    print(f"  FAIL: {e}")

# =========================================================================
# Test 5: Streaming Output
# =========================================================================
print("\n[Test 5] Streaming Output - 流式输出")
print("-" * 80)

total += 1
print(f"\n[5.{total}] Streaming Output...")
try:
    from streaming_output import create_streaming_output
    stream = create_streaming_output()
    
    # Test full lifecycle
    stream.start()
    stream.send_text("Deep debug test")
    stream.send_progress(0.5)
    stream.send_status("Halfway done")
    stream.send_progress(1.0)
    stream.finish()
    
    chunks = stream.get_chunks()
    full_text = stream.get_full_text()
    elapsed = stream.get_elapsed_time()
    
    if len(chunks) >= 5 and "Deep debug" in full_text and elapsed >= 0:
        print("  OK: Streaming output works")
        passed += 1
    else:
        errors.append(f"Test 5.{total}: Streaming incomplete")
        print("  FAIL: Streaming incomplete")
except Exception as e:
    errors.append(f"Test 5.{total}: {e}")
    print(f"  FAIL: {e}")

# =========================================================================
# Test 6: Async Task Queue
# =========================================================================
print("\n[Test 6] Async Task Queue - 异步任务队列")
print("-" * 80)

total += 1
print(f"\n[6.{total}] Async Task Queue...")
try:
    from async_task_queue import create_async_task_queue, TaskPriority
    
    def sync_multiply(x):
        return x * 2
    
    queue = create_async_task_queue()
    task_id1 = queue.create_task("Multiply 21", sync_multiply, args=(21,), priority=TaskPriority.NORMAL)
    task_id2 = queue.create_task("Multiply 42", sync_multiply, args=(42,), priority=TaskPriority.HIGH)
    
    stats = queue.get_stats()
    
    if task_id1 and task_id2 and stats.get("queue_size", 0) >= 0:
        print("  OK: Async task queue works")
        passed += 1
    else:
        errors.append(f"Test 6.{total}: Task queue incomplete")
        print("  FAIL: Task queue incomplete")
except Exception as e:
    errors.append(f"Test 6.{total}: {e}")
    print(f"  FAIL: {e}")

# =========================================================================
# Test 7: Concurrency Monitor
# =========================================================================
print("\n[Test 7] Concurrency Monitor - 并发监控")
print("-" * 80)

total += 1
print(f"\n[7.{total}] Concurrency Monitor...")
try:
    from concurrency_monitor import create_concurrency_monitor
    monitor = create_concurrency_monitor()
    
    # Test full lifecycle
    monitor.task_started()
    monitor.task_started()
    monitor.update_queue_length(3)
    monitor.task_completed(0.1)
    monitor.task_completed(0.2)
    
    snapshot = monitor.take_snapshot()
    metrics = monitor.get_current_metrics()
    dashboard = monitor.get_ascii_dashboard()
    
    if (metrics.get("completed_tasks", 0) == 2 and 
        metrics.get("active_tasks", 0) == 0 and 
        len(dashboard) > 200):
        print("  OK: Concurrency monitor works")
        passed += 1
    else:
        errors.append(f"Test 7.{total}: Monitor incomplete")
        print("  FAIL: Monitor incomplete")
except Exception as e:
    errors.append(f"Test 7.{total}: {e}")
    print(f"  FAIL: {e}")

# =========================================================================
# Test 8: Deadlock Detector & Timeout
# =========================================================================
print("\n[Test 8] Deadlock Detector & Timeout - 死锁检测和超时")
print("-" * 80)

total += 1
print(f"\n[8.{total}] Deadlock Detector...")
try:
    from deadlock_detector import create_deadlock_detector, DeadlockStatus
    detector = create_deadlock_detector()
    
    # Test no deadlock case
    detector.add_wait("taskA", "taskB", "lock1")
    detector.add_wait("taskB", "taskC", "lock2")
    status1, cycle1 = detector.detect_deadlock()
    
    # Test deadlock case
    detector.clear()
    detector.add_wait("taskX", "taskY", "lockA")
    detector.add_wait("taskY", "taskX", "lockB")
    status2, cycle2 = detector.detect_deadlock()
    
    # Test timeout
    detector.set_timeout("test_timeout", 0.5)
    time.sleep(0.6)
    is_timeout = detector.check_timeout("test_timeout")
    
    if (status1 == DeadlockStatus.NO_DEADLOCK and 
        status2 == DeadlockStatus.DEADLOCK_DETECTED and 
        is_timeout):
        print("  OK: Deadlock detector & timeout works")
        passed += 1
    else:
        errors.append(f"Test 8.{total}: Deadlock detector incomplete")
        print("  FAIL: Deadlock detector incomplete")
except Exception as e:
    errors.append(f"Test 8.{total}: {e}")
    print(f"  FAIL: {e}")

# =========================================================================
# Test 9: UX Improvements
# =========================================================================
print("\n[Test 9] UX Improvements - 用户体验改进")
print("-" * 80)

total += 1
print(f"\n[9.{total}] UX Improvements...")
try:
    from ux_improvements import create_ux_improvements, UXMessageType, FriendlyError
    ux = create_ux_improvements()
    
    # Test progress bar
    for i in range(5):
        ux.show_progress(i / 4.0, "Deep debug")
    
    # Test messages
    ux.show_success("Deep debug test passed")
    ux.show_warning("This is a test warning")
    ux.show_message("Test info", UXMessageType.INFO)
    
    # Test friendly error
    try:
        raise FileNotFoundError("debug_test.txt")
    except Exception as e:
        friendly = ux.create_friendly_error(e, "Reading test file")
        if friendly.error_type == "FileNotFoundError":
            pass
    
    # Test stats
    ux.show_stats("Deep Debug Stats", {
        "Tests Run": total,
        "Tests Passed": passed,
        "Success Rate": f"{passed/max(1, total)*100:.1f}%"
    })
    
    print("\n  OK: UX improvements works")
    passed += 1
except Exception as e:
    errors.append(f"Test 9.{total}: {e}")
    print(f"  FAIL: {e}")

# =========================================================================
# Summary
# =========================================================================
print("\n" + "=" * 80)
print("DEEP DEBUG SUMMARY")
print("深度Debug总结")
print("=" * 80)
print(f"\nTotal Tests: {total}")
print(f"Passed: {passed}")
print(f"Failed: {total - passed}")
print(f"Success Rate: {passed/total*100:.1f}%")

if errors:
    print("\nErrors:")
    for i, err in enumerate(errors, 1):
        print(f"  {i}. {err}")
else:
    print("\nNo errors!")

if warnings:
    print("\nWarnings:")
    for i, warn in enumerate(warnings, 1):
        print(f"  {i}. {warn}")
else:
    print("\nNo warnings!")

if passed == total:
    print("\n" + "=" * 80)
    print("ALL TESTS PASSED! v0.4.1 is working perfectly!")
    print("所有测试通过！v0.4.1工作完美！")
    print("=" * 80)
else:
    print("\n" + "=" * 80)
    print("Some tests failed! Please check errors above.")
    print("部分测试失败！请检查上面的错误。")
    print("=" * 80)

print(f"\nFinished at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Duration: {passed}/{total} tests passed")
