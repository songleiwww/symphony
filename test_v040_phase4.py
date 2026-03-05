#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test v0.4.0 Phase 4 - 测试v0.4.0 Phase 4功能
"""

import sys
import os
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Test v0.4.0 Phase 4")
print("=" * 60)

passed = 0
total = 0

# Test 1: Deadlock Detector
total += 1
print(f"\n[Test {total}] Deadlock Detector...")
try:
    from deadlock_detector import create_deadlock_detector
    detector = create_deadlock_detector()
    print("  OK: Deadlock detector created")
    passed += 1
except Exception as e:
    print(f"  FAIL: {e}")

# Test 2: UX Improvements
total += 1
print(f"\n[Test {total}] UX Improvements...")
try:
    from ux_improvements import create_ux_improvements
    ux = create_ux_improvements()
    print("  OK: UX improvements created")
    passed += 1
except Exception as e:
    print(f"  FAIL: {e}")

# Test 3: Deadlock no cycle
total += 1
print(f"\n[Test {total}] Deadlock no cycle...")
try:
    from deadlock_detector import create_deadlock_detector, DeadlockStatus
    
    detector = create_deadlock_detector()
    detector.add_wait("task1", "task2", "resourceA")
    detector.add_wait("task2", "task3", "resourceB")
    status, cycle = detector.detect_deadlock()
    if status == DeadlockStatus.NO_DEADLOCK:
        print("  OK: No deadlock detected correctly")
        passed += 1
    else:
        print(f"  FAIL: Unexpected status: {status}")
except Exception as e:
    print(f"  FAIL: {e}")

# Test 4: Timeout
total += 1
print(f"\n[Test {total}] Timeout...")
try:
    from deadlock_detector import create_deadlock_detector
    
    detector = create_deadlock_detector()
    detector.set_timeout("test_task", 0.5)
    time.sleep(0.3)
    before = detector.check_timeout("test_task")
    time.sleep(0.3)
    after = detector.check_timeout("test_task")
    
    if not before and after:
        print("  OK: Timeout works correctly")
        passed += 1
    else:
        print(f"  FAIL: Timeout incorrect - before={before}, after={after}")
except Exception as e:
    print(f"  FAIL: {e}")

# Test 5: UX progress
total += 1
print(f"\n[Test {total}] UX progress...")
try:
    from ux_improvements import create_ux_improvements
    
    ux = create_ux_improvements()
    # Just test that it doesn't crash
    for i in range(5):
        ux.show_progress(i / 4.0, "Test")
    print("\n  OK: Progress bar works")
    passed += 1
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
