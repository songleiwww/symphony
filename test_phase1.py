#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Phase 1 - Quick Wins
Check that all improvements work
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Testing Phase 1 - Quick Wins")
print("测试 Phase 1 - Quick Wins")
print("=" * 60)

passed = 0
total = 0

# Test 1: Quick Start Guide exists
total += 1
print("\nTest 1: Quick Start Guide...")
qs_file = Path("QUICKSTART.md")
if qs_file.exists():
    print("  OK: QUICKSTART.md exists")
    passed += 1
else:
    print("  FAIL: QUICKSTART.md missing")

# Test 2: Model Reporter exists
total += 1
print("\nTest 2: Model Reporter...")
mr_file = Path("model_reporter.py")
if mr_file.exists():
    print("  OK: model_reporter.py exists")
    passed += 1
else:
    print("  FAIL: model_reporter.py missing")

# Test 3: Examples directory exists
total += 1
print("\nTest 3: Examples directory...")
examples_dir = Path("examples")
if examples_dir.exists() and examples_dir.is_dir():
    print("  OK: examples/ directory exists")
    passed += 1
else:
    print("  FAIL: examples/ directory missing")

# Test 4: Examples have files
total += 1
print("\nTest 4: Example files...")
example_files = [
    "weather_final.py",
    "tianji_final.py",
    "model_discussion_final.py",
    "README.md"
]
found = 0
for f in example_files:
    if (examples_dir / f).exists():
        found += 1
        print(f"  OK: {f}")
if found >= 3:
    passed += 1
    print(f"  OK: Found {found} example files")
else:
    print(f"  FAIL: Only found {found} example files")

# Test 5: Model Reporter works
total += 1
print("\nTest 5: Model Reporter works...")
try:
    from model_reporter import create_reporter
    reporter = create_reporter()
    reporter.record_usage("Test Role", "test-model", "test-provider")
    reporter.record_tool_call(success=True)
    print("  OK: Model Reporter works")
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
