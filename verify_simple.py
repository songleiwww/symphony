#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Symphony System Verification Script - Simplified"""

import sys
import time
import json
import os

# Redirect stderr to suppress debug output
sys.stderr = open(os.devnull, 'w')

# Add symphony to path
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')

print("=" * 60)
print("[SYMPHONY SYSTEM VERIFICATION]")
print("=" * 60)

results = {}
perf_results = {}

# Test 1: Module Imports
print("\n[TEST 1] Module Import Test")

try:
    from symphony_core import SymphonyCore, MemoryItem
    results['symphony_core'] = 'PASS'
    print("  [OK] symphony_core")
except Exception as e:
    results['symphony_core'] = f'FAIL: {e}'
    print(f"  [FAIL] symphony_core: {e}")

try:
    from symphony_core_engine import SymphonyCoreEngine, Task, Model
    results['symphony_core_engine'] = 'PASS'
    print("  [OK] symphony_core_engine")
except Exception as e:
    results['symphony_core_engine'] = f'FAIL: {e}'
    print(f"  [FAIL] symphony_core_engine: {e}")

try:
    from smart_orchestrator import SmartOrchestrator
    results['smart_orchestrator'] = 'PASS'
    print("  [OK] smart_orchestrator")
except Exception as e:
    results['smart_orchestrator'] = f'FAIL: {e}'
    print(f"  [FAIL] smart_orchestrator: {e}")

import_pass = sum(1 for v in results.values() if v == 'PASS')
print(f"\nModule imports: {import_pass}/{len(results)} passed")

# Test 2: Basic Functionality
print("\n[TEST 2] Basic Functionality Test")
func_results = {}

# Test SymphonyCore
try:
    core = SymphonyCore(memory_path="test_memory.json")
    mem_id = core.add_memory("Test memory", "short_term", 0.8, ["test"], "general")
    mem = core.get_memory(mem_id)
    
    if mem and mem.id == mem_id:
        func_results['SymphonyCore'] = 'PASS'
        print("  [OK] SymphonyCore: Memory system working")
    else:
        func_results['SymphonyCore'] = 'FAIL'
        print("  [FAIL] SymphonyCore: Memory access failed")
except Exception as e:
    func_results['SymphonyCore'] = f'FAIL: {e}'
    print(f"  [FAIL] SymphonyCore: {e}")

# Test SymphonyCoreEngine
try:
    engine = SymphonyCoreEngine()
    
    test_model = Model(
        model_id="test_model",
        alias="Test",
        role="assistant",
        emoji="robot",
        specialty="testing"
    )
    engine.register_model(test_model)
    
    task = Task(
        task_id="test_001",
        description="Test task",
        assigned_to="",
        priority=1
    )
    engine.add_task(task)
    engine.assign_task("test_001", "test_model")
    engine.complete_task("test_001")
    
    stats = engine.get_stats()
    
    if stats['completed'] == 1:
        func_results['SymphonyCoreEngine'] = 'PASS'
        print("  [OK] SymphonyCoreEngine: Task scheduling working")
    else:
        func_results['SymphonyCoreEngine'] = 'FAIL'
        print("  [FAIL] SymphonyCoreEngine: Task status error")
except Exception as e:
    func_results['SymphonyCoreEngine'] = f'FAIL: {e}'
    print(f"  [FAIL] SymphonyCoreEngine: {e}")

func_pass = sum(1 for v in func_results.values() if v == 'PASS')
print(f"\nBasic functionality: {func_pass}/{len(func_results)} passed")

# Test 3: Performance Benchmark
print("\n[TEST 3] Performance Benchmark")

# Memory operations benchmark
try:
    core = SymphonyCore(memory_path="bench_memory.json")
    
    start = time.time()
    for i in range(100):
        core.add_memory(f"Benchmark {i}", "short_term", 0.5, ["bench"], "test")
    mem_time = time.time() - start
    
    perf_results['Memory Write (100 ops)'] = f'{mem_time*1000:.2f}ms'
    print(f"  [OK] Memory Write (100 ops): {mem_time*1000:.2f}ms")
    
    start = time.time()
    for i in range(100):
        core.get_memory(f"mem_{i+1}_0")
    read_time = time.time() - start
    
    perf_results['Memory Read (100 ops)'] = f'{read_time*1000:.2f}ms'
    print(f"  [OK] Memory Read (100 ops): {read_time*1000:.2f}ms")
except Exception as e:
    perf_results['Memory Benchmark'] = f'FAIL: {e}'
    print(f"  [FAIL] Memory Benchmark: {e}")

# Engine benchmark
try:
    engine = SymphonyCoreEngine()
    
    for i in range(10):
        engine.register_model(Model(
            model_id=f"model_{i}",
            alias=f"Model {i}",
            role="assistant",
            emoji="robot",
            specialty="test"
        ))
    
    start = time.time()
    for i in range(50):
        engine.add_task(Task(
            task_id=f"task_{i}",
            description=f"Task {i}",
            assigned_to="",
            priority=i % 3
        ))
    task_time = time.time() - start
    
    perf_results['Task Creation (50 ops)'] = f'{task_time*1000:.2f}ms'
    print(f"  [OK] Task Creation (50 ops): {task_time*1000:.2f}ms")
    
except Exception as e:
    perf_results['Engine Benchmark'] = f'FAIL: {e}'
    print(f"  [FAIL] Engine Benchmark: {e}")

# Summary
print("\n" + "=" * 60)
print("[VERIFICATION SUMMARY]")

all_pass = import_pass == len(results) and func_pass == len(func_results)
status = "pass" if all_pass else "fail"

total_tests = len(results) + len(func_results) + len(perf_results)
passed_tests = import_pass + func_pass + sum(1 for v in perf_results.values() if 'FAIL' not in v)
score = int((passed_tests / total_tests) * 100)

print(f"Status: {status.upper()}")
print(f"Score: {score}/100")

details = {
    "module_imports": results,
    "basic_functionality": func_results,
    "performance_benchmarks": perf_results
}

print(f"\nDetails:")
print(json.dumps(details, indent=2))

# Cleanup
for f in ['test_memory.json', 'bench_memory.json']:
    if os.path.exists(f):
        os.remove(f)

sys.stderr.close()

print("\n[VERIFICATION COMPLETE]")
