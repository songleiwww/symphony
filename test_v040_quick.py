#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test v0.4.0 Quick - 快速测试v0.4.0功能
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Test v0.4.0 - Quick Test")
print("=" * 60)

passed = 0
total = 0

# Test 1: Memory Importer/Exporter exists
total += 1
print(f"\n[Test {total}] Memory Importer/Exporter...")
try:
    from memory_importer_exporter import create_importer_exporter
    print("  OK: Importer/Exporter exists")
    passed += 1
except Exception as e:
    print(f"  FAIL: {e}")

# Test 2: Can create instance
total += 1
print(f"\n[Test {total}] Create importer/exporter...")
try:
    from memory_importer_exporter import create_importer_exporter
    ie = create_importer_exporter()
    print("  OK: Created successfully")
    passed += 1
except Exception as e:
    print(f"  FAIL: {e}")

# Test 3: Async Memory Core exists
total += 1
print(f"\n[Test {total}] Async Memory Core...")
try:
    from async_memory_core import create_improved_core
    print("  OK: Async core exists")
    passed += 1
except Exception as e:
    print(f"  FAIL: {e}")

# Test 4: Deep test exists
total += 1
print(f"\n[Test {total}] Deep test...")
try:
    deep_test = Path("deep_test_async.py")
    if deep_test.exists():
        print("  OK: Deep test exists")
        passed += 1
    else:
        print("  FAIL: Deep test missing")
except Exception as e:
    print(f"  FAIL: {e}")

# Test 5: Discussion exists
total += 1
print(f"\n[Test {total}] Discussion file...")
try:
    discussion = Path("symphony_deep_discussion.py")
    if discussion.exists():
        print("  OK: Discussion exists")
        passed += 1
    else:
        print("  FAIL: Discussion missing")
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
    print("\n✅ ALL TESTS PASSED!")
else:
    print("\n❌ Some tests failed!")

print("\n" + "=" * 60)
