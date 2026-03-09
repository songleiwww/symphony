#!/usr/bin/env python3
"""Symphony System Verification Script"""

import sys
import time
import json
import os

sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')

results = {}
func_results = {}
perf_results = {}

print("[SYMPHONY SYSTEM VERIFICATION]")

# Test 1: Module Imports
print("\n[TEST 1] Module Import")

# Test symphony_core_engine
try:
    from symphony_core_engine import SymphonyCoreEngine, Task, Model
    results['symphony_core_engine'] = 'PASS'
    print("  [OK] symphony_core_engine")
except Exception as e:
    results['symphony_core_engine'] = 'FAIL'
    print(f"  [FAIL] symphony_core_engine")

# Test memory_system
try:
    import memory_system
    results['memory_system'] = 'PASS'
    print("  [OK] memory_system")
except Exception as e:
    results['memory_system'] = 'FAIL'
    print(f"  [FAIL] memory_system")

# Test parallel_orchestrator
try:
    import parallel_orchestrator
    results['parallel_orchestrator'] = 'PASS'
    print("  [OK] parallel_orchestrator")
except Exception as e:
    results['parallel_orchestrator'] = 'FAIL'
    print(f"  [FAIL] parallel_orchestrator")

# Test dynamic_orchestrator
try:
    import dynamic_orchestrator
    results['dynamic_orchestrator'] = 'PASS'
    print("  [OK] dynamic_orchestrator")
except Exception as e:
    results['dynamic_orchestrator'] = 'FAIL'
    print(f"  [FAIL] dynamic_orchestrator")

# Test model_manager
try:
    import model_manager
    results['model_manager'] = 'PASS'
    print("  [OK] model_manager")
except Exception as e:
    results['model_manager'] = 'FAIL'
    print(f"  [FAIL] model_manager")

import_pass = sum(1 for v in results.values() if v == 'PASS')

# Test 2: Basic Functionality
print("\n[TEST 2] Basic Functionality")

# Test SymphonyCoreEngine
try:
    engine = SymphonyCoreEngine()
    test_model = Model(model_id="test", alias="T", role="a", emoji="r", specialty="s")
    engine.register_model(test_model)
    task = Task(task_id="t1", description="Test", assigned_to="", priority=1)
    engine.add_task(task)
    engine.assign_task("t1", "test")
    engine.complete_task("t1")
    stats = engine.get_stats()
    if stats['completed'] == 1:
        func_results['Task Scheduling'] = 'PASS'
        print("  [OK] Task Scheduling")
    else:
        func_results['Task Scheduling'] = 'FAIL'
except:
    func_results['Task Scheduling'] = 'FAIL'

# Test memory_system
try:
    mem = memory_system.MemorySystem(":memory:")
    mem_id = mem.add_memory("Test", "test", 0.8)
    retrieved = mem.get_memory(mem_id)
    if retrieved and retrieved['content'] == "Test":
        func_results['Memory System'] = 'PASS'
        print("  [OK] Memory System")
    else:
        func_results['Memory System'] = 'FAIL'
except:
    func_results['Memory System'] = 'FAIL'

func_pass = sum(1 for v in func_results.values() if v == 'PASS')

# Test 3: Performance Benchmark
print("\n[TEST 3] Performance Benchmark")

# Task Creation Benchmark
try:
    engine = SymphonyCoreEngine()
    for i in range(50):
        engine.register_model(Model(model_id=f"m{i}", alias=f"M{i}", role="a", emoji="r", specialty="s"))
    start = time.time()
    for i in range(200):
        engine.add_task(Task(task_id=f"t{i}", description=f"Task {i}", assigned_to="", priority=i%3))
    task_time = time.time() - start
    perf_results['Task Creation (200)'] = f'{task_time*1000:.2f}ms'
    print(f"  [OK] Task Creation: {task_time*1000:.2f}ms")
except:
    perf_results['Task Creation'] = 'FAIL'

# Memory Benchmark
try:
    mem = memory_system.MemorySystem(":memory:")
    start = time.time()
    for i in range(100):
        mem.add_memory(f"T{i}", "bench", 0.5)
    mem_time = time.time() - start
    perf_results['Memory Write (100)'] = f'{mem_time*1000:.2f}ms'
    
    start = time.time()
    for i in range(100):
        mem.get_memory(f"mem_{i}")
    read_time = time.time() - start
    perf_results['Memory Read (100)'] = f'{read_time*1000:.2f}ms'
    print(f"  [OK] Memory Write: {mem_time*1000:.2f}ms, Read: {read_time*1000:.2f}ms")
except:
    perf_results['Memory Benchmark'] = 'FAIL'

# Summary
total_tests = import_pass + func_pass + len(perf_results)
passed = import_pass + func_pass + sum(1 for v in perf_results.values() if 'FAIL' not in v)
score = int((passed / total_tests) * 100) if total_tests > 0 else 0
status = "pass" if import_pass >= 4 and func_pass >= 2 else "fail"

output = {
    "status": status,
    "score": score,
    "details": {
        "module_imports": results,
        "basic_functionality": func_results,
        "performance_benchmarks": perf_results
    }
}

print(f"\n[RESULT] Status: {status}, Score: {score}/100")
print(json.dumps(output, indent=2))
