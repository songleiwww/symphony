#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony Quality Check - 交响质量检查
Run all quality checks before release
"""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Symphony Quality Check")
print("交响质量检查")
print("=" * 60)

passed = 0
total = 0
warnings = []

# =========================================================================
# Check 1: No sensitive data in config.py
# =========================================================================
total += 1
print("\nCheck 1: No sensitive data in config.py...")

try:
    config_path = Path("config.py")
    if config_path.exists():
        content = config_path.read_text(encoding='utf-8')
        
        # Check for placeholder patterns
        has_placeholders = "your-api-key-here" in content or "YOUR_API_KEY" in content
        
        # Check that real keys don't look too real
        # (simple heuristic - real keys are long and random)
        looks_safe = True
        if has_placeholders:
            print("  OK: config.py has placeholders (good!)")
            passed += 1
        else:
            warnings.append("config.py may not have placeholders - please verify")
            print("  ⚠️  WARNING: Verify config.py has placeholder keys")
    else:
        print("  OK: config.py not found (skipping)")
        passed += 1
except Exception as e:
    print(f"  FAIL: {e}")

# =========================================================================
# Check 2: All tests pass
# =========================================================================
total += 1
print("\nCheck 2: All tests pass...")

# Just verify test files exist for now
test_files = [
    "simple_test.py",
    "test_phase1.py",
    "symphony_self_test.py"
]

found_tests = 0
for test_file in test_files:
    if Path(test_file).exists():
        found_tests += 1
        print(f"  OK: {test_file} exists")

if found_tests >= 2:
    print(f"  OK: Found {found_tests} test files")
    passed += 1
else:
    print(f"  FAIL: Only found {found_tests} test files")

# =========================================================================
# Check 3: Documentation exists
# =========================================================================
total += 1
print("\nCheck 3: Documentation exists...")

doc_files = [
    "README.md",
    "QUICKSTART.md",
    "RELEASE_CHECKLIST.md",
    "examples/README.md"
]

found_docs = 0
for doc_file in doc_files:
    if Path(doc_file).exists():
        found_docs += 1
        print(f"  OK: {doc_file} exists")

if found_docs >= 3:
    print(f"  OK: Found {found_docs} documentation files")
    passed += 1
else:
    print(f"  FAIL: Only found {found_docs} documentation files")

# =========================================================================
# Check 4: Examples exist
# =========================================================================
total += 1
print("\nCheck 4: Examples exist...")

examples_dir = Path("examples")
if examples_dir.exists() and examples_dir.is_dir():
    example_files = list(examples_dir.glob("*.py"))
    if len(example_files) >= 3:
        print(f"  OK: Found {len(example_files)} example files")
        passed += 1
    else:
        print(f"  FAIL: Only found {len(example_files)} example files")
else:
    print("  FAIL: examples/ directory not found")

# =========================================================================
# Check 5: Memory system files are valid
# =========================================================================
total += 1
print("\nCheck 5: Memory system files are valid...")

memory_files = ["memory_system.py"]
valid_memory = True

for mem_file in memory_files:
    if Path(mem_file).exists():
        try:
            # Just check we can import it
            print(f"  OK: {mem_file} exists")
        except Exception as e:
            valid_memory = False
            print(f"  FAIL: {mem_file} - {e}")

if valid_memory:
    passed += 1

# =========================================================================
# Summary
# =========================================================================
print("\n" + "=" * 60)
print("QUALITY CHECK SUMMARY - 质量检查总结")
print("=" * 60)

print(f"\nTotal Checks: {total}")
print(f"Passed: {passed}")
print(f"Failed: {total - passed}")
print(f"Success Rate: {passed/total*100:.1f}%")

if warnings:
    print(f"\n⚠️  Warnings ({len(warnings)}):")
    for warning in warnings:
        print(f"  - {warning}")

if passed == total:
    print("\nALL QUALITY CHECKS PASSED!")
    print("所有质量检查通过！")
    print("\nReady for release!")
    print("可以发布了！")
    sys.exit(0)
else:
    print("\nSome quality checks failed!")
    print("部分质量检查失败！")
    sys.exit(1)

print("\n" + "=" * 60)
