#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Phase 3 - Core Foundation (Memory Integration)
测试 Phase 3 - 核心基础（记忆集成）
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Testing Phase 3 - Core Foundation (Memory Integration)")
print("测试 Phase 3 - 核心基础（记忆集成）")
print("=" * 60)

passed = 0
total = 0

# Test 1: Symphony Core exists
total += 1
print("\nTest 1: Symphony Core...")
core_file = Path("symphony_core.py")
if core_file.exists():
    print("  OK: symphony_core.py exists")
    passed += 1
else:
    print("  FAIL: symphony_core.py missing")

# Test 2: Memory Visualizer exists
total += 1
print("\nTest 2: Memory Visualizer...")
viz_file = Path("memory_visualizer.py")
if viz_file.exists():
    print("  OK: memory_visualizer.py exists")
    passed += 1
else:
    print("  FAIL: memory_visualizer.py missing")

# Test 3: Symphony Core can be imported
total += 1
print("\nTest 3: Symphony Core import...")
try:
    from symphony_core import create_symphony_core
    print("  OK: Symphony Core imported")
    passed += 1
except Exception as e:
    print(f"  FAIL: {e}")

# Test 4: Memory Visualizer can be imported
total += 1
print("\nTest 4: Memory Visualizer import...")
try:
    from memory_visualizer import MemoryVisualizer
    print("  OK: Memory Visualizer imported")
    passed += 1
except Exception as e:
    print(f"  FAIL: {e}")

# Test 5: Symphony Core works
total += 1
print("\nTest 5: Symphony Core works...")
try:
    from symphony_core import create_symphony_core
    
    # Create core with test memory
    test_core = create_symphony_core("test_memory.json")
    
    # Add a memory
    mem_id = test_core.add_memory(
        "Test memory for Phase 3",
        "long_term",
        0.8,
        ["test", "phase3"],
        "test"
    )
    
    # Set a preference
    test_core.set_preference("test_mode", "on")
    
    # Get stats
    stats = test_core.get_stats()
    
    print(f"  OK: Symphony Core works!")
    print(f"    Memory added: {mem_id}")
    print(f"    Total memories: {stats['total_memories']}")
    passed += 1
    
    # Clean up
    if Path("test_memory.json").exists():
        Path("test_memory.json").unlink()
        
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
