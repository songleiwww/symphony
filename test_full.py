#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统完整测试脚本
"""
import sys
import os

# 设置路径
PROJECT_DIR = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony"
sys.path.insert(0, PROJECT_DIR)
os.chdir(PROJECT_DIR)

# 设置UTF-8输出
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("Symphony System Test")
print("=" * 60)

# 测试1: 数据库连接
print("\n[Test 1] Database Connection")
try:
    import sqlite3
    conn = sqlite3.connect(os.path.join(PROJECT_DIR, "data", "symphony.db"))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM 官属角色表")
    roles_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM 模型配置表")
    models_count = cursor.fetchone()[0]
    conn.close()
    print(f"  OK - Roles: {roles_count}, Models: {models_count}")
except Exception as e:
    print(f"  FAIL - {e}")

# 测试2: 内核加载
print("\n[Test 2] Kernel Loader")
try:
    from kernel.kernel_loader import KernelLoader
    kernel = KernelLoader()
    kernel.load_all()
    print(f"  OK - Loaded {len(kernel.roles)} roles, {len(kernel.models)} models")
except Exception as e:
    print(f"  FAIL - {e}")
    import traceback
    traceback.print_exc()

# 测试3: 任务管理器
print("\n[Test 3] Task Manager")
try:
    from core.task_manager import TaskManager, TaskStatus
    tm = TaskManager()
    task = tm.create_task(content="Test task", task_type="test")
    print(f"  OK - Created task: {task.task_id[:8]}...")
except Exception as e:
    print(f"  FAIL - {e}")

# 测试4: 记忆系统
print("\n[Test 4] Memory System")
try:
    from core.memory_system import MemorySystem
    ms = MemorySystem()
    mem_id = ms.add_memory(content="Test memory", memory_type="short_term")
    results = ms.search_memory("Test")
    print(f"  OK - Added memory: {mem_id}, Found: {len(results)}")
except Exception as e:
    print(f"  FAIL - {e}")

# 测试5: 容错系统
print("\n[Test 5] Fault Tolerance")
try:
    from core.fault_tolerance import FaultTolerance
    ft = FaultTolerance()
    ft.record_failure("test_model", "Test error")
    health = ft.get_model_health("test_model")
    print(f"  OK - Health: {health.get('health')}")
except Exception as e:
    print(f"  FAIL - {e}")

print("\n" + "=" * 60)
print("All Tests Completed!")
print("=" * 60)
