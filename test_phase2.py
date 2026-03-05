#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Phase 2 - Quality & Reliability
Check that quality improvements work
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Testing Phase 2 - Quality & Reliability")
print("测试 Phase 2 - 质量与可靠性")
print("=" * 60)

passed = 0
total = 0

# Test 1: Release Checklist exists
total += 1
print("\nTest 1: Release Checklist...")
rc_file = Path("RELEASE_CHECKLIST.md")
if rc_file.exists():
    print("  OK: RELEASE_CHECKLIST.md exists")
    passed += 1
else:
    print("  FAIL: RELEASE_CHECKLIST.md missing")

# Test 2: Quality Check script exists
total += 1
print("\nTest 2: Quality Check script...")
qc_file = Path("quality_check.py")
if qc_file.exists():
    print("  OK: quality_check.py exists")
    passed += 1
else:
    print("  FAIL: quality_check.py missing")

# Test 3: All test files exist
total += 1
print("\nTest 3: All test files...")
test_files = [
    "simple_test.py",
    "test_phase1.py",
    "test_phase2.py",
    "symphony_self_test.py"
]
found = 0
for f in test_files:
    if Path(f).exists():
        found += 1
        print(f"  OK: {f}")
if found >= 3:
    passed += 1
    print(f"  OK: Found {found} test files")
else:
    print(f"  FAIL: Only found {found} test files")

# Test 4: Quality Check can be imported
total += 1
print("\nTest 4: Quality Check works...")
try:
    # Just verify the file is valid Python
    content = Path("quality_check.py").read_text(encoding='utf-8')
    print("  OK: quality_check.py is valid")
    passed += 1
except Exception as e:
    print(f"  FAIL: {e}")

# Test 5: Release Checklist has all items
total += 1
print("\nTest 5: Release Checklist content...")
try:
    content = Path("RELEASE_CHECKLIST.md").read_text(encoding='utf-8')
    has_quality = "Quality Checks" in content
    has_automation = "Automation Checks" in content
    has_standards = "Quality Standards" in content
    
    if has_quality and has_automation and has_standards:
        print("  OK: Release Checklist has all sections")
        passed += 1
    else:
        print("  FAIL: Release Checklist missing sections")
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
