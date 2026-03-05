#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test v0.4.0 Phase 2 - 测试v0.4.0 Phase 2功能
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Test v0.4.0 Phase 2")
print("=" * 60)

passed = 0
total = 0

# Test 1: Context-aware Memory
total += 1
print(f"\n[Test {total}] Context-aware Memory...")
try:
    from context_aware_memory import create_context_aware_memory
    ctx = create_context_aware_memory()
    print("  OK: Context-aware memory created")
    passed += 1
except Exception as e:
    print(f"  FAIL: {e}")

# Test 2: Streaming Output
total += 1
print(f"\n[Test {total}] Streaming Output...")
try:
    from streaming_output import create_streaming_output
    stream = create_streaming_output()
    print("  OK: Streaming output created")
    passed += 1
except Exception as e:
    print(f"  FAIL: {e}")

# Test 3: Context initialization
total += 1
print(f"\n[Test {total}] Context initialization...")
try:
    from context_aware_memory import create_context_aware_memory
    ctx = create_context_aware_memory()
    summary = ctx.get_context_summary()
    if "session" in summary and "time_of_day" in summary["session"]:
        print("  OK: Context initialized")
        passed += 1
    else:
        print("  FAIL: Context incomplete")
except Exception as e:
    print(f"  FAIL: {e}")

# Test 4: User context
total += 1
print(f"\n[Test {total}] User context...")
try:
    from context_aware_memory import create_context_aware_memory
    ctx = create_context_aware_memory()
    ctx.set_user_context("test_key", "test_value")
    val = ctx.get_user_context("test_key")
    if val == "test_value":
        print("  OK: User context works")
        passed += 1
    else:
        print("  FAIL: User context incorrect")
except Exception as e:
    print(f"  FAIL: {e}")

# Test 5: Streaming start/finish
total += 1
print(f"\n[Test {total}] Streaming start/finish...")
try:
    from streaming_output import create_streaming_output
    stream = create_streaming_output()
    stream.start()
    stream.finish()
    print("  OK: Streaming start/finish works")
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
