#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import importlib.util

# 切换到项目根目录
project_dir = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony"
os.chdir(project_dir)
sys.path.insert(0, project_dir)

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("Symphony System Test")
print("=" * 60)

# Test 1: Database
print("\n[Test 1] Database")
import sqlite3
conn = sqlite3.connect("data/symphony.db")
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM 官属角色表")
roles = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM 模型配置表")
models = cursor.fetchone()[0]
conn.close()
print(f"  OK - Roles: {roles}, Models: {models}")

# Test 2: Kernel - load manually
print("\n[Test 2] Kernel Loader")
spec = importlib.util.spec_from_file_location("kernel_loader", "kernel/kernel_loader.py")
kernel_loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kernel_loader)
kernel = kernel_loader.get_kernel()
print(f"  OK - Roles: {len(kernel.roles)}, Models: {len(kernel.models)}")

# Test 3: Task Manager
print("\n[Test 3] Task Manager")
spec2 = importlib.util.spec_from_file_location("task_manager", "core/task_manager.py")
task_manager = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(task_manager)
tm = task_manager.get_task_manager()
task = tm.create_task(content="Test task")
print(f"  OK - Task: {task.task_id[:8]}")

# Test 4: Memory
print("\n[Test 4] Memory System")
spec3 = importlib.util.spec_from_file_location("memory_system", "core/memory_system.py")
memory_system = importlib.util.module_from_spec(spec3)
spec3.loader.exec_module(memory_system)
ms = memory_system.get_memory_system()
mem_id = ms.add_memory("Test memory", "short_term", 0.5)
print(f"  OK - Memory: {mem_id}")

# Test 5: Model Manager
print("\n[Test 5] Model Manager")
spec4 = importlib.util.spec_from_file_location("model_call_manager", "core/model_call_manager.py")
model_call_manager = importlib.util.module_from_spec(spec4)
spec4.loader.exec_module(model_call_manager)
mm = model_call_manager.get_model_manager()
print(f"  OK - Models loaded: {len(mm.model_configs)}")

print("\n" + "=" * 60)
print("All Core Modules PASSED!")
print("=" * 60)
